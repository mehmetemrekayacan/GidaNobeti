/**
 * Dashboard Page - Statistics & Charts
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui';
import { isAuthenticated } from '@/lib/auth';
import { apiClient } from '@/lib/api-client';
import { TrendingUp, Users, AlertCircle, UtensilsCrossed } from 'lucide-react';

interface DashboardStats {
  period: string;
  total_orders: number;
  total_students: number;
  total_incidents: number;
  top_restaurants: Array<{ name: string; order_count: number }>;
  incidents_by_restaurant: Array<{ restaurant: string; incident_count: number }>;
  daily_breakdown: Array<{ date: string; orders: number; incidents: number }>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Fetch dashboard statistics
    const fetchStats = async () => {
      try {
        const response = await apiClient.get('/admin/dashboard/statistics', {
          params: { period: 'last_7_days' }
        });
        setStats(response.data);
        setLoading(false);
      } catch (err: any) {
        console.error('Failed to fetch dashboard stats:', err);
        setError(err.response?.data?.detail || 'Veri yüklenirken hata oluştu');
        setLoading(false);
      }
    };

    fetchStats();
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Yükleniyor...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">Hata: {error}</div>
      </div>
    );
  }

  // Calculate risk restaurant count from stats
  const riskyRestaurantCount = stats?.incidents_by_restaurant?.length || 0;

  const statsCards = [
    {
      title: 'Toplam Sipariş',
      value: stats?.total_orders?.toLocaleString('tr-TR') || '0',
      change: '+12%', // TODO: Calculate from daily breakdown
      icon: TrendingUp,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Aktif Öğrenci',
      value: stats?.total_students?.toLocaleString('tr-TR') || '0',
      change: '+5%', // TODO: Calculate from daily breakdown
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Toplam Vaka',
      value: stats?.total_incidents?.toLocaleString('tr-TR') || '0',
      change: '-8%', // TODO: Calculate from daily breakdown
      icon: AlertCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Riskli Restoran',
      value: riskyRestaurantCount.toString(),
      change: '+2', // TODO: Calculate trend
      icon: UtensilsCrossed,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
  ];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Son 7 günlük özet</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsCards.map((stat) => (
          <Card key={stat.title} className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className={`text-sm mt-1 ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {stat.change} son 7 güne göre
                </p>
              </div>
              <div className={`${stat.bgColor} p-3 rounded-full`}>
                <stat.icon className={stat.color} size={24} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Günlük Sipariş Trendi
          </h2>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <p className="text-gray-500">Grafik yükleniyor... (Chart.js entegrasyonu)</p>
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            En Çok Sipariş Verilen Restoranlar
          </h2>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <p className="text-gray-500">Grafik yükleniyor... (Chart.js entegrasyonu)</p>
          </div>
        </Card>
      </div>

      {/* Info Alert */}
      <Card className="mt-6 bg-blue-50 border border-blue-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="text-blue-600 mt-1" size={20} />
          <div>
            <p className="text-sm font-medium text-blue-900">
              🚀 Admin Panel Başarıyla Kuruldu!
            </p>
            <p className="text-sm text-blue-700 mt-1">
              Backend API endpoint'leri tamamlandığında gerçek datalar burada görünecek.
              Şu anda frontend yapısı hazır ve çalışıyor.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
