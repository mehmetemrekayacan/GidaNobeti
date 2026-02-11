'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card } from '@/components/ui';
import { Search, Filter, Download, Calendar, Package } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface Order {
  id: string;
  studentName: string;
  restaurant: string;
  date: string;
  time: string;
  amount: number;
  method: 'SCREENSHOT' | 'RECEIPT' | 'PHYSICAL_RECEIPT' | 'MANUAL_ENTRY';
}

function mapApiOrder(api: { id: string; student_name: string; restaurant_name: string | null; declared_at: string; total_amount: number | null; method: string }): Order {
  const d = new Date(api.declared_at);
  return {
    id: api.id,
    studentName: api.student_name,
    restaurant: api.restaurant_name || '-',
    date: d.toISOString().split('T')[0],
    time: d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
    amount: api.total_amount ?? 0,
    method: api.method as Order['method'],
  };
}

// Fallback mock - API hata verirse
const mockOrders: Order[] = [
  {
    id: '1',
    studentName: 'Ahmet Yılmaz',
    restaurant: 'Pasaport Pizza',
    date: '2026-01-21',
    time: '19:45',
    amount: 85.50,
    method: 'SCREENSHOT',
  },
  {
    id: '2',
    studentName: 'Zeynep Kaya',
    restaurant: 'Burger King İzmir',
    date: '2026-01-21',
    time: '18:30',
    amount: 120.00,
    method: 'RECEIPT',
  },
  {
    id: '3',
    studentName: 'Mehmet Demir',
    restaurant: 'Dönerci Ahmet Usta',
    date: '2026-01-20',
    time: '20:15',
    amount: 65.00,
    method: 'SCREENSHOT',
  },
  {
    id: '4',
    studentName: 'Ayşe Öztürk',
    restaurant: 'Çiğ Köfteci Ramazan',
    date: '2026-01-20',
    time: '19:00',
    amount: 45.00,
    method: 'RECEIPT',
  },
  {
    id: '5',
    studentName: 'Can Şahin',
    restaurant: 'Pasaport Pizza',
    date: '2026-01-19',
    time: '21:00',
    amount: 95.00,
    method: 'SCREENSHOT',
  },
  {
    id: '6',
    studentName: 'Elif Yıldız',
    restaurant: 'Kahvaltı Durağı',
    date: '2026-01-19',
    time: '08:30',
    amount: 55.00,
    method: 'RECEIPT',
  },
  {
    id: '7',
    studentName: 'Burak Arslan',
    restaurant: 'Burger King İzmir',
    date: '2026-01-18',
    time: '19:45',
    amount: 110.00,
    method: 'SCREENSHOT',
  },
  {
    id: '8',
    studentName: 'Selin Çelik',
    restaurant: 'Dönerci Ahmet Usta',
    date: '2026-01-18',
    time: '20:30',
    amount: 70.00,
    method: 'RECEIPT',
  },
  {
    id: '9',
    studentName: 'Emre Koç',
    restaurant: 'Pasaport Pizza',
    date: '2026-01-17',
    time: '18:15',
    amount: 90.00,
    method: 'SCREENSHOT',
  },
  {
    id: '10',
    studentName: 'Deniz Aydın',
    restaurant: 'Çiğ Köfteci Ramazan',
    date: '2026-01-17',
    time: '19:30',
    amount: 50.00,
    method: 'RECEIPT',
  },
  {
    id: '11',
    studentName: 'Onur Tekin',
    restaurant: 'Burger King İzmir',
    date: '2026-01-16',
    time: '20:00',
    amount: 130.00,
    method: 'SCREENSHOT',
  },
  {
    id: '12',
    studentName: 'Merve Polat',
    restaurant: 'Kahvaltı Durağı',
    date: '2026-01-16',
    time: '09:00',
    amount: 60.00,
    method: 'RECEIPT',
  },
];

function OrdersTable({
  filteredOrders,
  orderIdParam,
  orders,
  itemsPerPage,
  getMethodBadge,
  rowRef,
}: {
  filteredOrders: Order[];
  orderIdParam: string | null;
  orders: Order[];
  itemsPerPage: number;
  getMethodBadge: (m: Order['method']) => React.ReactElement;
  rowRef: React.RefObject<HTMLTableRowElement | null>;
}) {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil(filteredOrders.length / itemsPerPage);
  const paginatedOrders = filteredOrders.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  useEffect(() => {
    if (orderIdParam && rowRef.current) {
      rowRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [orderIdParam, filteredOrders, rowRef]);

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Öğrenci</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Restoran</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Tarih & Saat</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Tutar</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Yöntem</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedOrders.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-16">
                  <div className="flex flex-col items-center justify-center gap-3 text-gray-500">
                    <Package className="w-12 h-12 text-gray-300" />
                    <p className="font-medium text-gray-600">
                      {orderIdParam ? 'Bu sipariş bulunamadı' : filteredOrders.length === 0 && orders.length === 0 ? 'Henüz sipariş yok' : 'Filtreye uygun sipariş bulunamadı'}
                    </p>
                    <p className="text-sm">
                      {orderIdParam ? 'Sipariş ID kontrol edin veya tüm siparişlere dönün.' : 'Farklı filtreler deneyin.'}
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              paginatedOrders.map((order) => (
                <tr
                  key={order.id}
                  ref={(el) => {
                    if (orderIdParam && String(order.id) === orderIdParam) {
                      (rowRef as React.MutableRefObject<HTMLTableRowElement | null>).current = el;
                    }
                  }}
                  className={`hover:bg-gray-50 ${orderIdParam && String(order.id) === orderIdParam ? 'bg-blue-200! ring-2 ring-blue-500 -ring-offset-2' : ''}`}
                >
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{order.studentName}</div>
                  </td>
                  <td className="px-6 py-4 text-gray-900">{order.restaurant}</td>
                  <td className="px-6 py-4">
                    <div className="text-gray-900">{order.date}</div>
                    <div className="text-sm text-gray-700">{order.time}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium text-gray-900">₺{order.amount.toFixed(2)}</span>
                  </td>
                  <td className="px-6 py-4">{getMethodBadge(order.method)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
          <div className="text-sm text-gray-700">
            <span className="font-medium">{filteredOrders.length}</span> sipariş bulundu
          </div>
          <div className="flex gap-2 items-center">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              Önceki
            </button>
            <div className="flex gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-3 py-1 rounded-lg font-medium ${currentPage === page ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  {page}
                </button>
              ))}
            </div>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              Sonraki
            </button>
          </div>
        </div>
      )}
    </Card>
  );
}

export default function OrdersPage() {
  const searchParams = useSearchParams();
  const orderIdParam = searchParams.get('order');
  const rowRef = useRef<HTMLTableRowElement | null>(null);

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDemoData, setIsDemoData] = useState(false);
  const [apiPage, setApiPage] = useState(1);
  const [totalFromApi, setTotalFromApi] = useState<number | null>(null);
  const [hasMorePages, setHasMorePages] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  const PAGE_SIZE = 100;

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        setIsDemoData(false);
        const res = await apiClient.get('/admin/orders', { params: { page: 1, limit: PAGE_SIZE } });
        const items = (res.data.items || []).map(mapApiOrder);
        const total = typeof res.data.total === 'number' ? res.data.total : items.length;
        setOrders(items);
        setTotalFromApi(total);
        setApiPage(1);
        setHasMorePages(items.length < total);
        setError(null);
      } catch {
        setOrders(mockOrders);
        setIsDemoData(true);
        setTotalFromApi(mockOrders.length);
        setApiPage(1);
        setHasMorePages(false);
        setError(null);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);
  const [searchQuery, setSearchQuery] = useState('');
  const [restaurantFilter, setRestaurantFilter] = useState('ALL');
  const [methodFilter, setMethodFilter] = useState('ALL');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const itemsPerPage = 10;

  // Filter key: when filters change, table remounts and page resets to 1 (no setState in effect)
  const filterKey = `${searchQuery}-${restaurantFilter}-${methodFilter}-${startDate}-${endDate}-${orderIdParam ?? ''}`;

  // Get unique restaurants for filter
  const uniqueRestaurants = Array.from(new Set(orders.map((o) => o.restaurant)));

  // Filter orders (derived state - no effect)
  const filteredOrders = useMemo(() => {
    let filtered = orders;

    if (orderIdParam) {
      filtered = filtered.filter(
        (o) => String(o.id) === orderIdParam || o.id.toString() === orderIdParam
      );
    }

    if (searchQuery && !orderIdParam) {
      filtered = filtered.filter(
        (o) =>
          o.studentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          o.restaurant.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (restaurantFilter !== 'ALL') {
      filtered = filtered.filter((o) => o.restaurant === restaurantFilter);
    }

    if (methodFilter !== 'ALL') {
      filtered = filtered.filter((o) => o.method === methodFilter);
    }

    if (startDate) filtered = filtered.filter((o) => o.date >= startDate);
    if (endDate) filtered = filtered.filter((o) => o.date <= endDate);

    return filtered;
  }, [searchQuery, restaurantFilter, methodFilter, startDate, endDate, orders, orderIdParam]);

  const getMethodBadge = (method: Order['method']) => {
    const styles: Record<string, string> = {
      SCREENSHOT: 'bg-blue-100 text-blue-800 border-blue-200',
      RECEIPT: 'bg-green-100 text-green-800 border-green-200',
      PHYSICAL_RECEIPT: 'bg-green-100 text-green-800 border-green-200',
      MANUAL_ENTRY: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    const labels: Record<string, string> = {
      SCREENSHOT: 'Ekran Görüntüsü',
      RECEIPT: 'Fiş',
      PHYSICAL_RECEIPT: 'Fiş',
      MANUAL_ENTRY: 'Manuel',
    };
    const style = styles[method] || 'bg-gray-100 text-gray-800 border-gray-200';
    const label = labels[method] || method;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
        {label}
      </span>
    );
  };

  const handleExportCSV = () => {
    // CSV headers
    const headers = ['ID', 'Öğrenci', 'Restoran', 'Tarih', 'Saat', 'Tutar', 'Yöntem'];
    
    // CSV rows
    const rows = filteredOrders.map((order) => [
      order.id,
      order.studentName,
      order.restaurant,
      order.date,
      order.time,
      order.amount.toFixed(2),
      order.method === 'SCREENSHOT' ? 'Ekran Görüntüsü' : 'Fiş',
    ]);

    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    // Create blob and download
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `siparisler_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const stats = {
    total: orders.length,
    totalAmount: orders.reduce((sum, o) => sum + o.amount, 0),
    screenshots: orders.filter((o) => o.method === 'SCREENSHOT').length,
    receipts: orders.filter((o) => o.method === 'RECEIPT').length,
  };

  const handleLoadMore = async () => {
    if (isDemoData || !hasMorePages || loadingMore) return;

    try {
      setLoadingMore(true);
      const nextPage = apiPage + 1;
      const res = await apiClient.get('/admin/orders', {
        params: { page: nextPage, limit: PAGE_SIZE },
      });
      const newItems = (res.data.items || []).map(mapApiOrder);
      const total = typeof res.data.total === 'number' ? res.data.total : totalFromApi ?? 0;

      setOrders((prev) => {
        const existingIds = new Set(prev.map((o) => o.id));
        const deduped = newItems.filter((o) => !existingIds.has(o.id));
        const merged = [...prev, ...deduped];
        setTotalFromApi(total || merged.length);
        setHasMorePages(merged.length < (total || merged.length));
        return merged;
      });

      setApiPage(nextPage);
    } catch (err) {
      console.error('Daha fazla sipariş yüklenirken hata oluştu', err);
    } finally {
      setLoadingMore(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Sipariş Yönetimi</h1>
        <div className="flex items-center justify-center py-16 text-gray-500">Yükleniyor...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Sipariş Yönetimi</h1>
        <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sipariş Yönetimi</h1>
          <p className="text-gray-700 mt-1">
            Tüm öğrenci siparişlerini görüntüleyin ve analiz edin
            {isDemoData && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
                Demo veri
              </span>
            )}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            Test: Vakalar sayfasında bir vakaya tıklayıp &quot;Sipariş&quot; linkine basın veya{' '}
            <a href="/dashboard/orders?order=1" className="text-blue-600 hover:underline">
              /dashboard/orders?order=1
            </a>{' '}
            ile belirli siparişe gidin.
          </p>
        </div>
        {orderIdParam && (
          <a
            href="/dashboard/orders"
            className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Tüm siparişlere dön
          </a>
        )}
        <button
          onClick={handleExportCSV}
          className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors"
        >
          <Download className="w-4 h-4" />
          CSV İndir
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600">Toplam Sipariş</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Toplam Tutar</div>
          <div className="text-2xl font-bold text-green-700">
            ₺{stats.totalAmount.toFixed(2)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-blue-600">Ekran Görüntüsü</div>
          <div className="text-2xl font-bold text-blue-700">{stats.screenshots}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-green-600">Fiş</div>
          <div className="text-2xl font-bold text-green-700">{stats.receipts}</div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="space-y-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Öğrenci adı veya restoran ara..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              />
            </div>
          </div>

          {/* Filter row */}
          <div className="flex flex-col md:flex-row gap-4">
            {/* Date range */}
            <div className="flex items-center gap-2 flex-1">
              <Calendar className="w-5 h-5 text-gray-400" />
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                placeholder="Başlangıç"
              />
              <span className="text-gray-500">-</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                placeholder="Bitiş"
              />
            </div>

            {/* Restaurant Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={restaurantFilter}
                onChange={(e) => setRestaurantFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              >
                <option value="ALL" className="text-gray-900 bg-white">Tüm Restoranlar</option>
                {uniqueRestaurants.map((restaurant) => (
                  <option key={restaurant} value={restaurant} className="text-gray-900 bg-white">
                    {restaurant}
                  </option>
                ))}
              </select>
            </div>

            {/* Method Filter */}
            <select
              value={methodFilter}
              onChange={(e) => setMethodFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
            >
              <option value="ALL" className="text-gray-900 bg-white">Tüm Yöntemler</option>
              <option value="SCREENSHOT" className="text-gray-900 bg-white">Ekran Görüntüsü</option>
              <option value="RECEIPT" className="text-gray-900 bg-white">Fiş</option>
              <option value="PHYSICAL_RECEIPT" className="text-gray-900 bg-white">Fiş (Fiziksel)</option>
              <option value="MANUAL_ENTRY" className="text-gray-900 bg-white">Manuel</option>
            </select>

            {/* Clear filters */}
            {(searchQuery || restaurantFilter !== 'ALL' || methodFilter !== 'ALL' || startDate || endDate) && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setRestaurantFilter('ALL');
                  setMethodFilter('ALL');
                  setStartDate('');
                  setEndDate('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium"
              >
                Temizle
              </button>
            )}
          </div>
        </div>
      </Card>

      {/* Load more & info (API paging) */}
      {!isDemoData && (
        <div className="flex items-center justify-between text-sm text-gray-700">
          <div>
            Yüklenen:{' '}
            <span className="font-medium">
              {orders.length}
            </span>
            {totalFromApi !== null && (
              <> / {totalFromApi}</>
            )}
          </div>
          {hasMorePages && (
            <button
              onClick={handleLoadMore}
              disabled={loadingMore}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60 font-medium transition-colors"
            >
              {loadingMore ? 'Yükleniyor...' : 'Daha fazla yükle'}
            </button>
          )}
        </div>
      )}

      {/* Table - key resets page to 1 when filters change */}
      <OrdersTable
        key={filterKey}
        filteredOrders={filteredOrders}
        orderIdParam={orderIdParam}
        orders={orders}
        itemsPerPage={itemsPerPage}
        getMethodBadge={getMethodBadge}
        rowRef={rowRef}
      />
    </div>
  );
}
