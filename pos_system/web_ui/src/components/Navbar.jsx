import React from 'react';
import { ShoppingBag, ShoppingCart, Package, BarChart3, Lock, Unlock, ShieldCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, isAdmin, onOpenAdminLogin, onLockAdmin }) {
  return (
    <nav className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <ShoppingBag size={22} />
        </div>
        <div className="brand-text">
          <h1>ABC SUPERMARKET POS</h1>
          <p>Point of Sale & Checkout Register</p>
        </div>
      </div>

      <div className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'pos' ? 'active' : ''}`}
          onClick={() => setActiveTab('pos')}
        >
          <ShoppingCart size={17} />
          POS Checkout
        </button>

        {isAdmin ? (
          <>
            <button
              className={`nav-tab ${activeTab === 'inventory' ? 'active' : ''}`}
              onClick={() => setActiveTab('inventory')}
            >
              <Package size={17} />
              Product Inventory (Admin)
            </button>
            <button
              className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <BarChart3 size={17} />
              Bill History & Sales (Admin)
            </button>
          </>
        ) : null}
      </div>

      <div>
        {isAdmin ? (
          <button className="admin-badge-btn unlocked" onClick={onLockAdmin} title="Click to Lock Admin Mode">
            <ShieldCheck size={16} />
            <span>Admin Active</span>
            <Unlock size={14} style={{ marginLeft: '0.2rem' }} />
          </button>
        ) : (
          <button className="admin-badge-btn locked" onClick={onOpenAdminLogin}>
            <Lock size={15} />
            <span>Admin Login</span>
          </button>
        )}
      </div>
    </nav>
  );
}
