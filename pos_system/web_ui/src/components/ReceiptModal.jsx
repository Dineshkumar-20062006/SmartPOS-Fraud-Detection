import React, { useState, useEffect } from 'react';
import { X, Printer, Download, CheckCircle2, Copy } from 'lucide-react';
import { fetchReceiptText, getReceiptPdfUrl } from '../api';

export default function ReceiptModal({ billNo, onClose }) {
  const [receiptText, setReceiptText] = useState('');
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (billNo) {
      setLoading(true);
      fetchReceiptText(billNo)
        .then((data) => {
          setReceiptText(data.receipt_text || '');
        })
        .catch((err) => {
          console.error('Error fetching receipt:', err);
          setReceiptText('Failed to load receipt.');
        })
        .finally(() => setLoading(false));
    }
  }, [billNo]);

  const handlePrint = () => {
    const printWin = window.open('', '_blank');
    printWin.document.write(`
      <html>
        <head>
          <title>Receipt #${billNo}</title>
          <style>
            body { font-family: monospace; padding: 20px; white-space: pre-wrap; }
          </style>
        </head>
        <body>
          <pre>${receiptText}</pre>
          <script>
            window.onload = function() { window.print(); window.close(); }
          </script>
        </body>
      </html>
    `);
    printWin.document.close();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(receiptText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!billNo) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-card" style={{ maxWidth: '560px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <CheckCircle2 color="#10B981" size={22} />
            <h3 style={{ fontSize: '1.1rem' }}>Transaction Completed</h3>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <p style={{ textAlign: 'center', color: '#94A3B8', padding: '2rem' }}>
              Generating receipt...
            </p>
          ) : (
            <div className="receipt-paper">
              {receiptText}
            </div>
          )}
        </div>

        <div className="modal-footer" style={{ justifyContent: 'space-between' }}>
          <button className="btn-secondary" onClick={handleCopy} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Copy size={16} />
            {copied ? 'Copied!' : 'Copy Text'}
          </button>

          <div style={{ display: 'flex', gap: '0.6rem' }}>
            <a
              href={getReceiptPdfUrl(billNo)}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', textDecoration: 'none' }}
            >
              <Download size={16} />
              PDF
            </a>
            <button className="btn-primary" onClick={handlePrint}>
              <Printer size={16} />
              Print Receipt
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
