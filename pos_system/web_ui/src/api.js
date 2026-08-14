const API_BASE = '/api';

export async function fetchProducts(search = '', includeInactive = false) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (includeInactive) params.append('include_inactive', 'true');

  const res = await fetch(`${API_BASE}/products?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export async function fetchLowStockProducts(threshold = 10) {
  const res = await fetch(`${API_BASE}/products/low-stock?threshold=${threshold}`);
  if (!res.ok) throw new Error('Failed to fetch low stock products');
  return res.json();
}

export async function addProduct(productData) {
  const res = await fetch(`${API_BASE}/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to add product');
  return data;
}

export async function updateProduct(id, productData) {
  const res = await fetch(`${API_BASE}/products/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to update product');
  return data;
}

export async function deleteProduct(id) {
  const res = await fetch(`${API_BASE}/products/${id}`, {
    method: 'DELETE'
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to delete product');
  return data;
}

export async function fetchNextBillNumber() {
  const res = await fetch(`${API_BASE}/bill/next-number`);
  if (!res.ok) throw new Error('Failed to generate bill number');
  return res.json();
}

export async function checkoutCart(checkoutData) {
  const res = await fetch(`${API_BASE}/bill/checkout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(checkoutData)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Checkout failed');
  return data;
}

export async function fetchBills(startDate = '', endDate = '') {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const res = await fetch(`${API_BASE}/bills?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch bill history');
  return res.json();
}

export async function fetchBillDetail(billNo) {
  const res = await fetch(`${API_BASE}/bills/${billNo}`);
  if (!res.ok) throw new Error('Bill not found');
  return res.json();
}

export async function fetchSalesAnalytics(startDate = '', endDate = '') {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const res = await fetch(`${API_BASE}/analytics?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch sales analytics');
  return res.json();
}

export async function fetchReceiptText(billNo) {
  const res = await fetch(`${API_BASE}/bills/${billNo}/receipt?format=txt`);
  if (!res.ok) throw new Error('Failed to fetch receipt text');
  return res.json();
}

export function getReceiptPdfUrl(billNo) {
  return `${API_BASE}/bills/${billNo}/receipt?format=pdf`;
}
