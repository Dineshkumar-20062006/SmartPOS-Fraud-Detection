import React, { useState, useEffect } from 'react';
import {
  Package,
  Plus,
  Edit2,
  Trash2,
  Search,
  CheckCircle,
  AlertTriangle,
  X,
  RefreshCw
} from 'lucide-react';
import {
  fetchProducts,
  addProduct,
  updateProduct,
  deleteProduct
} from '../api';

export default function ProductInventory() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [loading, setLoading] = useState(false);

  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({ name: '', price: '', stock: '' });
  const [formError, setFormError] = useState('');

  useEffect(() => {
    loadProducts();
  }, [includeInactive]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await fetchProducts('', includeInactive);
      setProducts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAdd = () => {
    setEditingProduct(null);
    setFormData({ name: '', price: '', stock: '' });
    setFormError('');
    setModalOpen(true);
  };

  const handleOpenEdit = (p) => {
    setEditingProduct(p);
    setFormData({ name: p.name, price: p.price, stock: p.stock });
    setFormError('');
    setModalOpen(true);
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!formData.name.trim()) {
      setFormError('Product name is required');
      return;
    }
    if (parseFloat(formData.price) <= 0 || isNaN(formData.price)) {
      setFormError('Price must be greater than 0');
      return;
    }
    if (parseInt(formData.stock) < 0 || isNaN(formData.stock)) {
      setFormError('Stock cannot be negative');
      return;
    }

    try {
      if (editingProduct) {
        await updateProduct(editingProduct.id, {
          name: formData.name,
          price: parseFloat(formData.price),
          stock: parseInt(formData.stock)
        });
      } else {
        await addProduct({
          name: formData.name,
          price: parseFloat(formData.price),
          stock: parseInt(formData.stock)
        });
      }
      setModalOpen(false);
      loadProducts();
    } catch (err) {
      setFormError(err.message || 'Failed to save product');
    }
  };

  const handleDelete = async (id, name) => {
    if (window.confirm(`Are you sure you want to deactivate product "${name}"?`)) {
      try {
        await deleteProduct(id);
        loadProducts();
      } catch (err) {
        alert(err.message);
      }
    }
  };

  const filteredProducts = products.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Control Bar */}
      <div style={{
        background: '#FFF',
        border: '1px solid #CBD5E1',
        borderRadius: '4px',
        padding: '0.85rem 1.1rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flex: 1 }}>
          <div className="search-input-group" style={{ maxWidth: '340px', flex: 1 }}>
            <Search className="search-icon-pos" size={16} />
            <input
              type="text"
              placeholder="Search product inventory..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.88rem', color: '#475569', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
            />
            Include Inactive Products
          </label>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn-trad-action" onClick={loadProducts} title="Refresh">
            <RefreshCw size={14} />
          </button>
          <button className="btn-trad-primary" onClick={handleOpenAdd}>
            + Add New Product
          </button>
        </div>
      </div>

      {/* Traditional Table */}
      <div className="trad-table-container">
        <table className="trad-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product Name</th>
              <th>Unit Price</th>
              <th>Current Stock</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredProducts.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: '#64748B' }}>
                  No inventory records match the current filter.
                </td>
              </tr>
            ) : (
              filteredProducts.map((p) => (
                <tr key={p.id}>
                  <td style={{ fontFamily: 'monospace' }}>#{p.id}</td>
                  <td style={{ fontWeight: 600 }}>{p.name}</td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 'bold', color: '#16A34A' }}>
                    ${p.price.toFixed(2)}
                  </td>
                  <td>
                    <span className={`prod-stock-tag ${p.stock === 0 ? 'zero' : p.stock <= 10 ? 'low' : 'ok'}`}>
                      {p.stock} units
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 'bold', fontSize: '0.8rem', color: p.is_active ? '#166534' : '#64748B' }}>
                      {p.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.4rem' }}>
                      <button className="btn-trad-action" onClick={() => handleOpenEdit(p)}>
                        Edit
                      </button>
                      {p.is_active && (
                        <button
                          className="btn-trad-action"
                          onClick={() => handleDelete(p.id, p.name)}
                          style={{ color: '#DC2626' }}
                        >
                          Deactivate
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add / Edit Modal */}
      {modalOpen && (
        <div className="modal-overlay-trad">
          <div className="modal-box-trad">
            <div className="modal-head-trad">
              <h3 style={{ margin: 0 }}>{editingProduct ? 'Edit Inventory Product' : 'Add New Inventory Product'}</h3>
              <button onClick={() => setModalOpen(false)} style={{ background: 'none', border: 'none', color: '#FFF', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} style={{ padding: '1.25rem' }}>
              {formError && (
                <div style={{ padding: '0.5rem', background: '#FEE2E2', border: '1px solid #FCA5A5', color: '#991B1B', borderRadius: '4px', fontSize: '0.85rem', marginBottom: '1rem' }}>
                  {formError}
                </div>
              )}

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.3rem' }}>Product Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  style={{ width: '100%', padding: '0.55rem', border: '1px solid #CBD5E1', borderRadius: '4px' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem', marginBottom: '1.25rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.3rem' }}>Unit Price ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    style={{ width: '100%', padding: '0.55rem', border: '1px solid #CBD5E1', borderRadius: '4px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.3rem' }}>Initial Stock</label>
                  <input
                    type="number"
                    value={formData.stock}
                    onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                    style={{ width: '100%', padding: '0.55rem', border: '1px solid #CBD5E1', borderRadius: '4px' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn-trad-action" onClick={() => setModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn-trad-primary">Save Product</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
