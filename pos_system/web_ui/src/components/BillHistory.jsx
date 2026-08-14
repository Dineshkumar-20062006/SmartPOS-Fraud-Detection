import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  FileText,
  TrendingUp,
  Search,
  Calendar,
  Eye
} from 'lucide-react';
import { fetchBills, fetchSalesAnalytics } from '../api';
import ReceiptModal from './ReceiptModal';

export default function BillHistory() {
  const [bills, setBills] = useState([]);
  const [analytics, setAnalytics] = useState({
    total_revenue: 0,
    total_bills: 0,
    avg_bill: 0,
    payment_breakdown: { Cash: 0, Card: 0, UPI: 0 }
  });

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [searchNo, setSearchNo] = useState('');
  const [selectedBillNo, setSelectedBillNo] = useState(null);

  useEffect(() => {
    loadData();
  }, [startDate, endDate]);

  const loadData = async () => {
    try {
      const [billsData, statsData] = await Promise.all([
        fetchBills(startDate, endDate),
        fetchSalesAnalytics(startDate, endDate)
      ]);
      setBills(billsData);
      setAnalytics(statsData);
    } catch (err) {
      console.error(err);
    }
  };

  const filteredBills = bills.filter((b) =>
    b.bill_no.toLowerCase().includes(searchNo.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Metric Cards Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <div style={{ background: '#FFF', border: '1px solid #CBD5E1', padding: '1rem', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.82rem', color: '#64748B', fontWeight: 600 }}>Total Revenue</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#16A34A', fontFamily: 'monospace' }}>
            ${analytics.total_revenue.toFixed(2)}
          </div>
        </div>

        <div style={{ background: '#FFF', border: '1px solid #CBD5E1', padding: '1rem', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.82rem', color: '#64748B', fontWeight: 600 }}>Total Bills Count</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#2563EB', fontFamily: 'monospace' }}>
            {analytics.total_bills}
          </div>
        </div>

        <div style={{ background: '#FFF', border: '1px solid #CBD5E1', padding: '1rem', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.82rem', color: '#64748B', fontWeight: 600 }}>Average Order Value</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A', fontFamily: 'monospace' }}>
            ${analytics.avg_bill.toFixed(2)}
          </div>
        </div>

        <div style={{ background: '#FFF', border: '1px solid #CBD5E1', padding: '1rem', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.82rem', color: '#64748B', fontWeight: 600 }}>Payment Method Totals</div>
          <div style={{ fontSize: '0.85rem', marginTop: '0.4rem', color: '#334155' }}>
            Cash: <b>${(analytics.payment_breakdown?.Cash || 0).toFixed(2)}</b> | Card: <b>${(analytics.payment_breakdown?.Card || 0).toFixed(2)}</b> | UPI: <b>${(analytics.payment_breakdown?.UPI || 0).toFixed(2)}</b>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div style={{
        background: '#FFF',
        border: '1px solid #CBD5E1',
        borderRadius: '4px',
        padding: '0.85rem 1.1rem',
        display: 'flex',
        gap: '0.85rem',
        alignItems: 'center',
        flexWrap: 'wrap'
      }}>
        <div className="search-input-group" style={{ width: '220px' }}>
          <Search className="search-icon-pos" size={16} />
          <input
            type="text"
            placeholder="Search Bill #"
            value={searchNo}
            onChange={(e) => setSearchNo(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: '#475569' }}>
          From:
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            style={{ padding: '0.4rem', border: '1px solid #CBD5E1', borderRadius: '4px' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: '#475569' }}>
          To:
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            style={{ padding: '0.4rem', border: '1px solid #CBD5E1', borderRadius: '4px' }}
          />
        </div>

        {(startDate || endDate || searchNo) && (
          <button className="btn-trad-action" onClick={() => { setStartDate(''); setEndDate(''); setSearchNo(''); }}>
            Reset Filter
          </button>
        )}
      </div>

      {/* History Table */}
      <div className="trad-table-container">
        <table className="trad-table">
          <thead>
            <tr>
              <th>Bill #</th>
              <th>Date</th>
              <th>Time</th>
              <th>Payment Method</th>
              <th>Total Amount</th>
              <th>Paid Amount</th>
              <th>Change</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredBills.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '2rem', color: '#64748B' }}>
                  No transaction records found matching filter.
                </td>
              </tr>
            ) : (
              filteredBills.map((b) => (
                <tr key={b.bill_no}>
                  <td style={{ fontFamily: 'monospace', fontWeight: 'bold', color: '#2563EB' }}>#{b.bill_no}</td>
                  <td>{b.bill_date}</td>
                  <td>{b.bill_time}</td>
                  <td><b>{b.payment_method}</b></td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>${b.total_amount.toFixed(2)}</td>
                  <td>${b.paid_amount.toFixed(2)}</td>
                  <td>${b.change_amount.toFixed(2)}</td>
                  <td>
                    <button className="btn-trad-action" onClick={() => setSelectedBillNo(b.bill_no)}>
                      Inspect Receipt
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedBillNo && (
        <ReceiptModal
          billNo={selectedBillNo}
          onClose={() => setSelectedBillNo(null)}
        />
      )}
    </div>
  );
}
