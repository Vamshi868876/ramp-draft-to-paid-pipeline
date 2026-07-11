import datetime
from ramp_api import RampAPI


ramp = RampAPI()



def auto_pay():


    print("Fetching Draft bills from Ramp...")

    try:
        draft_bills = ramp.get_draft_bills()
        
        # Filter the bills manually in Python to find Drafts/Unapproved
        bills_data = [
            b for b in draft_bills.get("data", [])
            if b.get("status") in ["OPEN", "DRAFT", "UNAPPROVED"]
        ]
        
        if not bills_data:
            print("No draft bills found.")
            return

        for draft in bills_data:
            draft_id = draft.get("id")
            invoice_num = draft.get("invoice_number", "UNKNOWN")
            
            print(f"\nProcessing Draft Bill: {draft_id} (Invoice: {invoice_num})")
            
            # Step 1: Extract necessary data
            vendor_id = draft.get("vendor", {}).get("id")
            if not vendor_id:
                print(f"SKIPPING: Draft {draft_id} has no Vendor ID (Ramp OCR could not match a vendor). Please fix manually in dashboard.")
                continue

            invoice_number = draft.get("invoice_number", "").strip()
            if not invoice_number:
                print(f"SKIPPING: Draft {draft_id} is missing an Invoice Number (Ramp OCR failed). Please fix manually in dashboard.")
                continue

            # Clean line items for POST schema
            clean_line_items = []
            for item in draft.get("line_items", []):
                # Extract amount from nested dict (e.g. 1408000 cents -> 14080.00)
                amount_data = item.get("amount", {})
                raw_amount = amount_data.get("amount", 0)
                minor_unit = amount_data.get("minor_unit_conversion_rate", 100)
                flat_amount = raw_amount / minor_unit if minor_unit else raw_amount
                
                clean_item = {
                    "amount": flat_amount,
                    "memo": item.get("memo", "Imported from draft"),
                }
                clean_line_items.append(clean_item)

            issued_at_str = draft.get("issued_at")[:10] if draft.get("issued_at") else None
            
            # Enforce Net 45 terms if issued_at is available
            due_at_str = draft.get("due_at")[:10] if draft.get("due_at") else None
            if issued_at_str:
                try:
                    issued_date = datetime.datetime.strptime(issued_at_str, "%Y-%m-%d")
                    due_date = issued_date + datetime.timedelta(days=45)
                    due_at_str = due_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass

            new_bill_payload = {
                "invoice_number": draft.get("invoice_number"),
                "issued_at": issued_at_str,
                "due_at": due_at_str,
                "invoice_currency": draft.get("currency", "USD"),
                "entity_id": draft.get("entity_id"), 
                "vendor_id": vendor_id,
                "memo": draft.get("memo", "Auto-generated from draft"),
                "line_items": clean_line_items,
                "use_default_payment_method": True,
                "use_default_vendor_contact": True
            }

            # Clean up None values if API rejects them
            new_bill_payload = {k: v for k, v in new_bill_payload.items() if v is not None}

            print(f"Attempting to create Paid Bill with payload: {new_bill_payload}")
            
            # Step 2: Create the new paid bill directly (Ramp API does not support deleting drafts)
            print(f"Recreating bill as Approved/Paid via ACH...")
            try:
                result = ramp.create_and_pay_bill(new_bill_payload)
                print("SUCCESS! New Paid Bill ID:", result.get("id"))
            except Exception as e:
                error_msg = str(e)
                if hasattr(e, 'response') and e.response is not None:
                    error_msg = e.response.text
                
                if "already exists" in error_msg:
                    print(f"SKIPPING: A bill for invoice '{draft.get('invoice_number')}' already exists. Ignoring this ghost draft.")
                else:
                    print(f"ERROR: Failed to create new bill! Payload was: {new_bill_payload}")
                    print(f"API Details: {error_msg}")

    except Exception as e:
        print(f"Error during auto_pay process: {e}")
