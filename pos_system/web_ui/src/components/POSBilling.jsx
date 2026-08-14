import React, { useState, useEffect } from 'react';
import {
  Search,
  Plus,
  Minus,
  Trash2,
  AlertCircle
} from 'lucide-react';
import { fetchProducts, fetchNextBillNumber, checkoutCart } from '../api';
import ReceiptModal from './ReceiptModal';

export default function POSBilling() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [cart, setCart] = useState([]);
  const [billNo, setBillNo] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Cash');
  const [paidAmount, setPaidAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [completedBillNo, setCompletedBillNo] = useState(null);

  useEffect(() => {
    loadProducts();
    loadNextBillNo();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await fetchProducts('', false);
      setProducts(data);
    } catch (err) {
      console.error(err);
      setErrorMsg('Failed to load product catalog');
    }
  };

  const loadNextBillNo = async () => {
    try {
      const res = await fetchNextBillNumber();
      setBillNo(res.bill_no);
    } catch (err) {
      console.error(err);
    }
  };

  const filteredProducts = products.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  const addToCart = (product) => {
    if (product.stock <= 0) {
      setErrorMsg(`Product "${product.name}" is out of stock!`);
      setTimeout(() => setErrorMsg(''), 3000);
      return;
    }

    setCart((prevCart) => {
      const existing = prevCart.find((item) => item.product_id === product.id);
      if (existing) {
        if (existing.quantity >= product.stock) {
          setErrorMsg(`Stock limit reached for "${product.name}"`);
          setTimeout(() => setErrorMsg(''), 3000);
          return prevCart;
        }
        return prevCart.map((item) =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [
          ...prevCart,
          {
            product_id: product.id,
            name: product.name,
            price: product.price,
            stock: product.stock,
            quantity: 1
          }
        ];
      }
    });
  };

  const updateQuantity = (productId, delta) => {
    setCart((prevCart) =>
      prevCart
        .map((item) => {
          if (item.product_id === productId) {
            const newQty = item.quantity + delta;
            if (newQty > item.stock) {
              setErrorMsg(`Stock limit reached for "${item.name}"`);
              setTimeout(() => setErrorMsg(''), 3000);
              return item;
            }
            return newQty > 0 ? { ...item, quantity: newQty } : null;
          }
          return item;
        })
        .filter(Boolean)
    );
  };

  const removeFromCart = (productId) => {
    setCart((prevCart) => prevCart.filter((item) => item.product_id !== productId));
  };

  const calculateSubtotal = () => {
    return cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  const totalAmount = calculateSubtotal();
  const numericPaid = parseFloat(paidAmount) || 0;
  const changeGiven = paymentMethod === 'Cash' ? Math.max(0, numericPaid - totalAmount) : 0;

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setErrorMsg('Cart is empty!');
      setTimeout(() => setErrorMsg(''), 3000);
      return;
    }

    if (paymentMethod === 'Cash' && numericPaid < totalAmount) {
      setErrorMsg(`Paid amount ($${numericPaid.toFixed(2)}) is less than total ($${totalAmount.toFixed(2)})`);
      setTimeout(() => setErrorMsg(''), 4000);
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const checkoutPayload = {
        cart_items: cart.map((c) => ({ product_id: c.product_id, quantity: c.quantity })),
        bill_no: billNo,
        paid_amount: paymentMethod === 'Cash' ? numericPaid : totalAmount,
        payment_method: paymentMethod
      };

      const result = await checkoutCart(checkoutPayload);
      if (result.success) {
        setCompletedBillNo(result.bill.bill_no);
        setCart([]);
        setPaidAmount('');
        loadProducts();
        loadNextBillNo();
      }
    } catch (err) {
      setErrorMsg(err.message || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pos-container">
      {/* Product Selection List Table */}
      <div className="traditional-card catalog-section">
        <div className="card-header">
          <h2>Product List Catalog</h2>
          <span style={{ fontSize: '0.85rem', color: '#64748B' }}>
            Click item row to add to billing ledger
          </span>
        </div>

        <div className="search-bar">
          <div className="search-input-group">
            <Search className="search-icon-pos" size={18} />
            <input
              type="text"
              placeholder="Search products by name or code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {errorMsg && (
          <div style={{
            margin: '0.5rem 1rem',
            padding: '0.6rem 0.85rem',
            background: '#FEE2E2',
            border: '1px solid #FCA5A5',
            borderRadius: '4px',
            color: '#991B1B',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}>
            <AlertCircle size={16} />
            {errorMsg}
          </div>
        )}

        {/* List View Table */}
        <div className="product-list-wrapper">
          <table className="trad-table" style={{ fontSize: '0.9rem' }}>
            <thead>
              <tr>
                <th style={{ width: '60px' }}>ID</th>
                <th>Product Name</th>
                <th>Unit Price</th>
                <th>Available Stock</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748B' }}>
                    No products found matching "{search}"
                  </td>
                </tr>
              ) : (
                filteredProducts.map((p) => {
                  const isOutStock = p.stock === 0;
                  const isLowStock = p.stock > 0 && p.stock <= 10;

                  return (
                    <tr
                      key={p.id}
                      className={`prod-list-row ${isOutStock ? 'disabled' : ''}`}
                      onClick={() => !isOutStock && addToCart(p)}
                    >
                      <td style={{ fontFamily: 'monospace', color: '#64748B' }}>#{p.id}</td>
                      <td style={{ fontWeight: 600 }}>{p.name}</td>
                      <td style={{ fontFamily: 'monospace', fontWeight: 'bold', color: '#16A34A' }}>
                        ${p.price.toFixed(2)}
                      </td>
                      <td>
                        <span className={`prod-stock-tag ${isOutStock ? 'zero' : isLowStock ? 'low' : 'ok'}`}>
                          {isOutStock ? 'Out of Stock' : `${p.stock} units`}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          type="button"
                          className="btn-trad-primary"
                          style={{ padding: '0.3rem 0.75rem', fontSize: '0.8rem' }}
                          disabled={isOutStock}
                          onClick={(e) => {
                            e.stopPropagation();
                            addToCart(p);
                          }}
                        >
                          + Add
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cashier Billing Ledger & Checkout Panel */}
      <div className="traditional-card cart-section">
        <div className="card-header">
          <h2>Cashier Checkout Register</h2>
          <span style={{ fontFamily: 'monospace', fontWeight: 'bold', color: '#2563EB' }}>
            Bill #{billNo}
          </span>
        </div>

        <div className="cart-table-wrapper">
          <table className="cart-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Price</th>
                <th style={{ textAlign: 'center' }}>Qty</th>
                <th style={{ textAlign: 'right' }}>Total</th>
                <th style={{ width: '32px' }}></th>
              </tr>
            </thead>
            <tbody>
              {cart.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '3rem 1rem', color: '#94A3B8' }}>
                    Billing register is currently empty.
                  </td>
                </tr>
              ) : (
                cart.map((item) => (
                  <tr key={item.product_id}>
                    <td style={{ fontWeight: 600 }}>{item.name}</td>
                    <td>${item.price.toFixed(2)}</td>
                    <td style={{ textAlign: 'center' }}>
                      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <button className="qty-btn-trad" onClick={() => updateQuantity(item.product_id, -1)}>-</button>
                        <span style={{ minWidth: '20px', fontWeight: 'bold' }}>{item.quantity}</span>
                        <button className="qty-btn-trad" onClick={() => updateQuantity(item.product_id, 1)}>+</button>
                      </div>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 'bold', fontFamily: 'monospace' }}>
                      ${(item.price * item.quantity).toFixed(2)}
                    </td>
                    <td>
                      <button
                        onClick={() => removeFromCart(item.product_id)}
                        style={{ border: 'none', background: 'transparent', color: '#DC2626', cursor: 'pointer' }}
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="checkout-panel-bottom">
          <div className="total-due-row">
            <span style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#475569' }}>Total Due:</span>
            <span className="total-due-price">${totalAmount.toFixed(2)}</span>
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', marginBottom: '0.3rem', display: 'block' }}>
              Payment Method
            </label>
            <div className="pay-options-row">
              <button
                className={`pay-btn-trad ${paymentMethod === 'Cash' ? 'selected' : ''}`}
                onClick={() => setPaymentMethod('Cash')}
              >
                💵 Cash
              </button>
              <button
                className={`pay-btn-trad ${paymentMethod === 'Card' ? 'selected' : ''}`}
                onClick={() => setPaymentMethod('Card')}
              >
                💳 Card
              </button>
              <button
                className={`pay-btn-trad ${paymentMethod === 'UPI' ? 'selected' : ''}`}
                onClick={() => setPaymentMethod('UPI')}
              >
                📱 UPI
              </button>
            </div>
          </div>

          {paymentMethod === 'Cash' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', alignItems: 'center' }}>
              <input
                type="number"
                step="0.01"
                placeholder="Cash Tendered ($)"
                value={paidAmount}
                onChange={(e) => setPaidAmount(e.target.value)}
                style={{
                  padding: '0.55rem',
                  border: '1px solid #CBD5E1',
                  borderRadius: '4px',
                  fontFamily: 'monospace',
                  fontSize: '1rem',
                  fontWeight: 'bold'
                }}
              />
              <div style={{
                padding: '0.55rem',
                background: '#DCFCE7',
                border: '1px solid #86EFAC',
                borderRadius: '4px',
                fontSize: '0.85rem',
                fontWeight: 'bold',
                color: '#166534',
                textAlign: 'center'
              }}>
                Change: ${changeGiven.toFixed(2)}
              </div>
            </div>
          )}

          <button
            className="checkout-btn"
            disabled={cart.length === 0 || loading}
            onClick={handleCheckout}
          >
            {loading ? 'Processing...' : 'Complete Sale & Print Receipt'}
          </button>
        </div>
      </div>

      {completedBillNo && (
        <ReceiptModal
          billNo={completedBillNo}
          onClose={() => setCompletedBillNo(null)}
        />
      )}
    </div>
  );
}
