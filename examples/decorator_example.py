import logging
import sys
from pathlib import Path

# Add the src directory to the Python path if not already there (for local development)
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tracelight.decorators import traced

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("decorator_example")

@traced(logger=logger)
def process_order(order_data):
    """Process an e-commerce order with automatic error tracing."""
    
    # Extract order information
    customer_id = order_data["customer_id"]
    items = order_data["items"]
    shipping_address = order_data.get("shipping_address", {})
    
    # Calculate totals
    subtotal = 0
    for item in items:
        price = float(item["price"])  # This might fail if price is not a number
        quantity = int(item["quantity"])  # This might fail if quantity is not a number
        subtotal += price * quantity
    
    # Apply tax
    tax_rate = 0.08
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    # Validate shipping address
    required_fields = ["street", "city", "state", "zip_code"]
    for field in required_fields:
        if field not in shipping_address:
            raise ValueError(f"Missing required shipping field: {field}")
    
    # Process payment (simulate)
    if total > 10000:  # Simulate a payment limit
        raise ValueError(f"Order total ${total:.2f} exceeds maximum allowed amount")
    
    # Return processed order
    return {
        "order_id": f"ORD-{customer_id}-{hash(str(order_data)) % 10000:04d}",
        "customer_id": customer_id,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total": total,
        "status": "processed"
    }

def main():
    print("\n🛍️ Testing order processing with automatic error tracing\n")
    
    # Test cases
    orders = [
        # Valid order
        {
            "customer_id": "CUST123",
            "items": [
                {"name": "Widget", "price": "29.99", "quantity": "2"},
                {"name": "Gadget", "price": "15.50", "quantity": "1"}
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345"
            }
        },
        
        # Order with invalid price
        {
            "customer_id": "CUST456",
            "items": [
                {"name": "Widget", "price": "invalid_price", "quantity": "1"}
            ],
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Somewhere",
                "state": "NY",
                "zip_code": "67890"
            }
        },
        
        # Order with missing shipping info
        {
            "customer_id": "CUST789",
            "items": [
                {"name": "Expensive Item", "price": "99.99", "quantity": "1"}
            ],
            "shipping_address": {
                "street": "789 Pine Rd",
                "city": "Elsewhere"
                # Missing state and zip_code
            }
        },
        
        # Order that's too expensive
        {
            "customer_id": "CUST999",
            "items": [
                {"name": "Luxury Item", "price": "15000.00", "quantity": "1"}
            ],
            "shipping_address": {
                "street": "999 Gold St",
                "city": "Rich Town",
                "state": "CA",
                "zip_code": "90210"
            }
        }
    ]
    
    for i, order in enumerate(orders, 1):
        print(f"Processing order {i} for customer {order['customer_id']}...")
        
        try:
            result = process_order(order)
            print(f"✅ Order processed successfully: {result['order_id']} - Total: ${result['total']:.2f}")
        except Exception as e:
            print(f"❌ Order failed: {type(e).__name__}: {e}")
            print("🔍 Error details have been logged with all local variables")
        
        print("-" * 60)
    
    print("\n✅ All orders processed. Check the logs for detailed error traces.")

if __name__ == "__main__":
    main()
