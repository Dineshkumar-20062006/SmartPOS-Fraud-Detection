import React, { useState } from 'react';
import Navbar from './components/Navbar';
import POSBilling from './components/POSBilling';
import ProductInventory from './components/ProductInventory';
import BillHistory from './components/BillHistory';
import AdminLoginModal from './components/AdminLoginModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('pos');
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminModalOpen, setAdminModalOpen] = useState(false);

  const handleOpenAdminLogin = () => {
    setAdminModalOpen(true);
  };

  const handleAdminSuccess = () => {
    setIsAdmin(true);
    setAdminModalOpen(false);
  };

  const handleLockAdmin = () => {
    setIsAdmin(false);
    setActiveTab('pos');
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isAdmin={isAdmin}
        onOpenAdminLogin={handleOpenAdminLogin}
        onLockAdmin={handleLockAdmin}
      />

      <main className="main-content">
        {activeTab === 'pos' && <POSBilling />}
        {isAdmin && activeTab === 'inventory' && <ProductInventory />}
        {isAdmin && activeTab === 'history' && <BillHistory />}
      </main>

      {adminModalOpen && (
        <AdminLoginModal
          onClose={() => setAdminModalOpen(false)}
          onSuccess={handleAdminSuccess}
        />
      )}
    </div>
  );
}
