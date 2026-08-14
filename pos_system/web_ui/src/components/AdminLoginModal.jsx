import React, { useState } from 'react';
import { Lock, X, KeyRound, ShieldAlert } from 'lucide-react';

export default function AdminLoginModal({ onClose, onSuccess }) {
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');

  const handleKeyClick = (digit) => {
    if (pin.length < 6) {
      setPin((prev) => prev + digit);
      setError('');
    }
  };

  const handleClear = () => {
    setPin('');
    setError('');
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (pin === '2006') {
      onSuccess();
    } else {
      setError('Invalid Admin PIN');
      setPin('');
    }
  };

  return (
    <div className="modal-overlay-trad">
      <div className="modal-box-trad" style={{ maxWidth: '380px' }}>
        <div className="modal-head-trad">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Lock size={20} />
            <h3 style={{ fontSize: '1.05rem', margin: 0 }}>Administrator Verification</h3>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#FFF', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
          <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: '#EFF6FF',
              color: '#2563EB',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 0.75rem'
            }}>
              <KeyRound size={24} />
            </div>
            <p style={{ fontSize: '0.88rem', color: '#475569' }}>
              Enter Admin Passcode to access Product Inventory & Bill History
            </p>
          </div>

          {error && (
            <div style={{
              padding: '0.6rem 0.8rem',
              background: '#FEE2E2',
              color: '#991B1B',
              border: '1px solid #FCA5A5',
              borderRadius: '4px',
              fontSize: '0.82rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}>
              <ShieldAlert size={16} />
              {error}
            </div>
          )}

          <div style={{ marginBottom: '1.25rem' }}>
            <input
              type="password"
              placeholder="Enter Admin PIN"
              value={pin}
              maxLength={6}
              onChange={(e) => {
                setPin(e.target.value);
                setError('');
              }}
              style={{
                width: '100%',
                padding: '0.75rem',
                textAlign: 'center',
                fontSize: '1.4rem',
                letterSpacing: '0.3em',
                fontFamily: 'monospace',
                border: '1px solid #CBD5E1',
                borderRadius: '4px',
                outline: 'none'
              }}
              autoFocus
            />
          </div>

          {/* Touch Keypad */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '0.5rem',
            marginBottom: '1.25rem'
          }}>
            {['1', '2', '3', '4', '5', '6', '7', '8', '9', 'CLR', '0', 'OK'].map((btn) => (
              <button
                key={btn}
                type="button"
                onClick={() => {
                  if (btn === 'CLR') handleClear();
                  else if (btn === 'OK') handleSubmit();
                  else handleKeyClick(btn);
                }}
                style={{
                  padding: '0.75rem',
                  fontSize: '1rem',
                  fontWeight: '700',
                  border: '1px solid #CBD5E1',
                  background: btn === 'OK' ? '#2563EB' : btn === 'CLR' ? '#F1F5F9' : '#FFFFFF',
                  color: btn === 'OK' ? '#FFFFFF' : '#0F172A',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                {btn}
              </button>
            ))}
          </div>

          <button
            type="submit"
            className="btn-trad-primary"
            style={{ width: '100%', padding: '0.75rem', fontSize: '1rem' }}
          >
            Unlock Admin Privileges
          </button>
        </form>
      </div>
    </div>
  );
}
