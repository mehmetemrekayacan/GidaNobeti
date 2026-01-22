'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import { Search, Filter, Download, Calendar } from 'lucide-react';

interface Order {
  id: number;
  studentName: string;
  restaurant: string;
  date: string;
  time: string;
  amount: number;
  method: 'SCREENSHOT' | 'RECEIPT';
}

// Mock data - Backend hazır olunca API'den gelecek
const mockOrders: Order[] = [
  {
    id: 1,
    studentName: 'Ahmet Yılmaz',
    restaurant: 'Pasaport Pizza',
    date: '2026-01-21',
    time: '19:45',
    amount: 85.50,
    method: 'SCREENSHOT',
  },
  {
    id: 2,
    studentName: 'Zeynep Kaya',
    restaurant: 'Burger King İzmir',
    date: '2026-01-21',
    time: '18:30',
    amount: 120.00,
    method: 'RECEIPT',
  },
  {
    id: 3,
    studentName: 'Mehmet Demir',
    restaurant: 'Dönerci Ahmet Usta',
    date: '2026-01-20',
    time: '20:15',
    amount: 65.00,
    method: 'SCREENSHOT',
  },
  {
    id: 4,
    studentName: 'Ayşe Öztürk',
    restaurant: 'Çiğ Köfteci Ramazan',
    date: '2026-01-20',
    time: '19:00',
    amount: 45.00,
    method: 'RECEIPT',
  },
  {
    id: 5,
    studentName: 'Can Şahin',
    restaurant: 'Pasaport Pizza',
    date: '2026-01-19',
    time: '21:00',
    amount: 95.00,
    method: 'SCREENSHOT',
  },
  {
    id: 6,
    studentName: 'Elif Yıldız',
    restaurant: 'Kahvaltı Durağı',
    date: '2026-01-19',
    time: '08:30',
    amount: 55.00,
    method: 'RECEIPT',
  },
  {
    id: 7,
    studentName: 'Burak Arslan',
    restaurant: 'Burger King İzmir',
    date: '2026-01-18',
    time: '19:45',
    amount: 110.00,
    method: 'SCREENSHOT',
  },
  {
    id: 8,
    studentName: 'Selin Çelik',
    restaurant: 'Dönerci Ahmet Usta',
    date: '2026-01-18',
    time: '20:30',
    amount: 70.00,
    method: 'RECEIPT',
  },
  {
    id: 9,
    studentName: 'Emre Koç',
    restaurant: 'Pasaport Pizza',
    date: '2026-01-17',
    time: '18:15',
    amount: 90.00,
    method: 'SCREENSHOT',
  },
  {
    id: 10,
    studentName: 'Deniz Aydın',
    restaurant: 'Çiğ Köfteci Ramazan',
    date: '2026-01-17',
    time: '19:30',
    amount: 50.00,
    method: 'RECEIPT',
  },
  {
    id: 11,
    studentName: 'Onur Tekin',
    restaurant: 'Burger King İzmir',
    date: '2026-01-16',
    time: '20:00',
    amount: 130.00,
    method: 'SCREENSHOT',
  },
  {
    id: 12,
    studentName: 'Merve Polat',
    restaurant: 'Kahvaltı Durağı',
    date: '2026-01-16',
    time: '09:00',
    amount: 60.00,
    method: 'RECEIPT',
  },
];

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>(mockOrders);
  const [filteredOrders, setFilteredOrders] = useState<Order[]>(mockOrders);
  const [searchQuery, setSearchQuery] = useState('');
  const [restaurantFilter, setRestaurantFilter] = useState('ALL');
  const [methodFilter, setMethodFilter] = useState('ALL');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Get unique restaurants for filter
  const uniqueRestaurants = Array.from(new Set(orders.map((o) => o.restaurant)));

  // Filter orders
  useEffect(() => {
    let filtered = orders;

    // Search by student name or restaurant
    if (searchQuery) {
      filtered = filtered.filter(
        (o) =>
          o.studentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          o.restaurant.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by restaurant
    if (restaurantFilter !== 'ALL') {
      filtered = filtered.filter((o) => o.restaurant === restaurantFilter);
    }

    // Filter by method
    if (methodFilter !== 'ALL') {
      filtered = filtered.filter((o) => o.method === methodFilter);
    }

    // Filter by date range
    if (startDate) {
      filtered = filtered.filter((o) => o.date >= startDate);
    }
    if (endDate) {
      filtered = filtered.filter((o) => o.date <= endDate);
    }

    setFilteredOrders(filtered);
    setCurrentPage(1); // Reset to first page on filter change
  }, [searchQuery, restaurantFilter, methodFilter, startDate, endDate, orders]);

  // Pagination
  const totalPages = Math.ceil(filteredOrders.length / itemsPerPage);
  const paginatedOrders = filteredOrders.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const getMethodBadge = (method: Order['method']) => {
    const styles = {
      SCREENSHOT: 'bg-blue-100 text-blue-800 border-blue-200',
      RECEIPT: 'bg-green-100 text-green-800 border-green-200',
    };

    const labels = {
      SCREENSHOT: 'Ekran Görüntüsü',
      RECEIPT: 'Fiş',
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[method]}`}
      >
        {labels[method]}
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sipariş Yönetimi</h1>
          <p className="text-gray-600 mt-1">
            Tüm öğrenci siparişlerini görüntüleyin ve analiz edin
          </p>
        </div>
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

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Öğrenci
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Restoran
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tarih & Saat
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tutar
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Yöntem
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedOrders.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    Sonuç bulunamadı
                  </td>
                </tr>
              ) : (
                paginatedOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{order.studentName}</div>
                    </td>
                    <td className="px-6 py-4 text-gray-900">{order.restaurant}</td>
                    <td className="px-6 py-4">
                      <div className="text-gray-900">{order.date}</div>
                      <div className="text-sm text-gray-500">{order.time}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-gray-900">
                        ₺{order.amount.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-6 py-4">{getMethodBadge(order.method)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
            <div className="text-sm text-gray-700">
              <span className="font-medium">{filteredOrders.length}</span> sipariş bulundu
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Önceki
              </button>
              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-1 rounded-lg font-medium ${
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Sonraki
              </button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
