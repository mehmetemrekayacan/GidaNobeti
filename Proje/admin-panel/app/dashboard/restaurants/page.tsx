'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import { Search, AlertTriangle, CheckCircle, XCircle, Edit2, Filter } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface Restaurant {
  id: number;
  name: string;
  riskStatus: 'SAFE' | 'WATCHLIST' | 'RED_FLAG' | 'BLACKLISTED';
  totalOrders: number;
  totalComplaints: number;
  riskReason?: string;
  platformOrigin?: string;
  lastIncidentDate?: string;
}

// Mock data - Backend hazır olunca API'den gelecek
const mockRestaurants: Restaurant[] = [
  {
    id: 1,
    name: 'Pasaport Pizza',
    riskStatus: 'SAFE',
    totalOrders: 245,
    totalComplaints: 2,
    platformOrigin: 'Getir',
  },
  {
    id: 2,
    name: 'Burger King İzmir',
    riskStatus: 'WATCHLIST',
    totalOrders: 189,
    totalComplaints: 12,
    riskReason: 'Son 7 günde 5 şikayet',
    platformOrigin: 'Yemeksepeti',
    lastIncidentDate: '2026-01-20',
  },
  {
    id: 3,
    name: 'Dönerci Ahmet Usta',
    riskStatus: 'RED_FLAG',
    totalOrders: 156,
    totalComplaints: 28,
    riskReason: 'Son 24 saatte 4 şikayet - gıda zehirlenmesi',
    platformOrigin: 'Getir',
    lastIncidentDate: '2026-01-21',
  },
  {
    id: 4,
    name: 'Çiğ Köfteci Ramazan',
    riskStatus: 'SAFE',
    totalOrders: 312,
    totalComplaints: 3,
    platformOrigin: 'Yemeksepeti',
  },
  {
    id: 5,
    name: 'Kahvaltı Durağı',
    riskStatus: 'BLACKLISTED',
    totalOrders: 78,
    totalComplaints: 45,
    riskReason: 'Ruhsat iptal - işletme kapatıldı',
    platformOrigin: 'Bilinmiyor',
    lastIncidentDate: '2026-01-18',
  },
];

export default function RestaurantsPage() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [filteredRestaurants, setFilteredRestaurants] = useState<Restaurant[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<'complaints' | 'orders' | 'name'>('complaints');
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch restaurants from API
  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        const response = await apiClient.get('/restaurants', {
          params: { limit: 100 }
        });
        
        // Transform API response to local format
        const transformed = response.data.map((r: any) => ({
          id: r.id,
          name: r.name,
          riskStatus: r.current_risk_status,
          totalOrders: r.total_orders || 0,
          totalComplaints: r.total_complaints || 0,
          riskReason: r.risk_reason,
          platformOrigin: r.platform_origin,
        }));
        
        setRestaurants(transformed);
        setLoading(false);
      } catch (err: any) {
        console.error('Failed to fetch restaurants:', err);
        setError(err.response?.data?.detail || 'Restoranlar yüklenirken hata oluştu');
        setLoading(false);
      }
    };

    fetchRestaurants();
  }, []);

  // Search & Filter
  useEffect(() => {
    let filtered = restaurants;

    // Search by name
    if (searchQuery) {
      filtered = filtered.filter((r) =>
        r.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by risk status
    if (riskFilter !== 'ALL') {
      filtered = filtered.filter((r) => r.riskStatus === riskFilter);
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      if (sortBy === 'complaints') return b.totalComplaints - a.totalComplaints;
      if (sortBy === 'orders') return b.totalOrders - a.totalOrders;
      if (sortBy === 'name') return a.name.localeCompare(b.name, 'tr');
      return 0;
    });

    setFilteredRestaurants(filtered);
  }, [searchQuery, riskFilter, sortBy, restaurants]);

  const getRiskBadge = (status: Restaurant['riskStatus']) => {
    const styles = {
      SAFE: 'bg-green-100 text-green-800 border-green-200',
      WATCHLIST: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      RED_FLAG: 'bg-red-100 text-red-800 border-red-200',
      BLACKLISTED: 'bg-gray-900 text-white border-gray-900',
    };

    const icons = {
      SAFE: <CheckCircle className="w-4 h-4" />,
      WATCHLIST: <AlertTriangle className="w-4 h-4" />,
      RED_FLAG: <XCircle className="w-4 h-4" />,
      BLACKLISTED: <XCircle className="w-4 h-4" />,
    };

    const labels = {
      SAFE: 'Güvenli',
      WATCHLIST: 'İzlemede',
      RED_FLAG: 'Riskli',
      BLACKLISTED: 'Yasaklı',
    };

    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${styles[status]}`}
      >
        {icons[status]}
        {labels[status]}
      </span>
    );
  };

  const handleEditClick = (restaurant: Restaurant) => {
    setSelectedRestaurant(restaurant);
    setShowEditModal(true);
  };

  const handleSaveRisk = async (newStatus: Restaurant['riskStatus'], reason: string) => {
    if (!selectedRestaurant) return;

    try {
      // Update via API
      await apiClient.put(`/admin/restaurants/${selectedRestaurant.id}/risk-status`, null, {
        params: {
          new_status: newStatus,
          reason: reason || undefined
        }
      });

      // Update local state
      const updated = restaurants.map((r) =>
        r.id === selectedRestaurant.id
          ? { ...r, riskStatus: newStatus, riskReason: reason }
          : r
      );
      setRestaurants(updated);
      setShowEditModal(false);
      setSelectedRestaurant(null);
    } catch (err: any) {
      console.error('Failed to update restaurant risk status:', err);
      alert('Risk durumu güncellenirken hata oluştu: ' + (err.response?.data?.detail || err.message));
    }
  };

  const stats = {
    total: restaurants.length,
    safe: restaurants.filter((r) => r.riskStatus === 'SAFE').length,
    watchlist: restaurants.filter((r) => r.riskStatus === 'WATCHLIST').length,
    risky: restaurants.filter((r) => r.riskStatus === 'RED_FLAG').length,
    blacklisted: restaurants.filter((r) => r.riskStatus === 'BLACKLISTED').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Restoran Yönetimi</h1>
        <p className="text-gray-600 mt-1">
          Risk durumlarını yönetin ve restoranları inceleyin
        </p>
      </div>

      {loading && (
        <div className="text-center py-8 text-gray-600">Yükleniyor...</div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          Hata: {error}
        </div>
      )}

      {!loading && !error && (
        <>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600">Toplam</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-green-600">Güvenli</div>
          <div className="text-2xl font-bold text-green-700">{stats.safe}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-yellow-600">İzlemede</div>
          <div className="text-2xl font-bold text-yellow-700">{stats.watchlist}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-red-600">Riskli</div>
          <div className="text-2xl font-bold text-red-700">{stats.risky}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Yasaklı</div>
          <div className="text-2xl font-bold text-gray-900">{stats.blacklisted}</div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Restoran adı ara..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Risk Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
            >
              <option value="ALL" className="text-gray-900 bg-white">Tüm Durumlar</option>
              <option value="SAFE" className="text-gray-900 bg-white">Güvenli</option>
              <option value="WATCHLIST" className="text-gray-900 bg-white">İzlemede</option>
              <option value="RED_FLAG" className="text-gray-900 bg-white">Riskli</option>
              <option value="BLACKLISTED" className="text-gray-900 bg-white">Yasaklı</option>
            </select>
          </div>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
          >
            <option value="complaints" className="text-gray-900 bg-white">Şikayet Sayısı</option>
            <option value="orders" className="text-gray-900 bg-white">Sipariş Sayısı</option>
            <option value="name" className="text-gray-900 bg-white">İsim (A-Z)</option>
          </select>
        </div>
      </Card>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Restoran
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Durumu
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sipariş
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Şikayet
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  İşlem
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredRestaurants.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    Sonuç bulunamadı
                  </td>
                </tr>
              ) : (
                filteredRestaurants.map((restaurant) => (
                  <tr key={restaurant.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium text-gray-900">{restaurant.name}</div>
                        {restaurant.riskReason && (
                          <div className="text-sm text-gray-500 mt-1">{restaurant.riskReason}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">{getRiskBadge(restaurant.riskStatus)}</td>
                    <td className="px-6 py-4 text-gray-900">{restaurant.totalOrders}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`font-medium ${
                          restaurant.totalComplaints > 20
                            ? 'text-red-600'
                            : restaurant.totalComplaints > 10
                            ? 'text-yellow-600'
                            : 'text-gray-900'
                        }`}
                      >
                        {restaurant.totalComplaints}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{restaurant.platformOrigin}</td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleEditClick(restaurant)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                        Düzenle
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Edit Modal */}
      {showEditModal && selectedRestaurant && (
        <EditRiskModal
          restaurant={selectedRestaurant}
          onClose={() => {
            setShowEditModal(false);
            setSelectedRestaurant(null);
          }}
          onSave={handleSaveRisk}
        />
      )}
        </>
      )}
    </div>
  );
}

// Edit Risk Modal Component
function EditRiskModal({
  restaurant,
  onClose,
  onSave,
}: {
  restaurant: Restaurant;
  onClose: () => void;
  onSave: (status: Restaurant['riskStatus'], reason: string) => void;
}) {
  const [status, setStatus] = useState<Restaurant['riskStatus']>(restaurant.riskStatus);
  const [reason, setReason] = useState(restaurant.riskReason || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(status, reason);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Risk Durumunu Güncelle</h2>
        <p className="text-gray-600 mb-6">{restaurant.name}</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Status Select */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Risk Durumu
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as Restaurant['riskStatus'])}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
            >
              <option value="SAFE" className="text-gray-900 bg-white">Güvenli</option>
              <option value="WATCHLIST" className="text-gray-900 bg-white">İzlemede</option>
              <option value="RED_FLAG" className="text-gray-900 bg-white">Riskli</option>
              <option value="BLACKLISTED" className="text-gray-900 bg-white">Yasaklı</option>
            </select>
          </div>

          {/* Reason Textarea */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Risk Nedeni / Açıklama
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={4}
              placeholder="Risk durumu değişikliğinin nedenini açıklayın..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
            >
              İptal
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
            >
              Kaydet
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
