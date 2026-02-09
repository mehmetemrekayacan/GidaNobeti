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
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface DashboardStats {
  period: string;
  total_orders: number;
  total_students: number;
  total_incidents: number;
  top_restaurants: Array<{ name: string; order_count: number }>;
  incidents_by_restaurant: Array<{ restaurant: string; incident_count: number }>;
  daily_breakdown: Array<{ date: string; orders: number; incidents: number }>;
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' });
}

function calcTrend(
  data: Array<{ orders?: number; incidents?: number }>,
  key: 'orders' | 'incidents'
): string {
  if (!data || data.length < 2) return '—';
  const half = Math.floor(data.length / 2);
  const firstHalf = data.slice(0, half).reduce((s, i) => s + (i[key] || 0), 0);
  const secondHalf = data.slice(half).reduce((s, i) => s + (i[key] || 0), 0);
  if (firstHalf === 0) return secondHalf > 0 ? '+100%' : '—';
  const pct = Math.round(((secondHalf - firstHalf) / firstHalf) * 100);
  return pct >= 0 ? `+${pct}%` : `${pct}%`;
}

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchStats = async () => {
      try {
        const response = await apiClient.get('/admin/dashboard/statistics', {
          params: { period: 'last_7_days' },
        });
        setStats(response.data);
      } catch (err: unknown) {
        const e = err as { response?: { data?: { detail?: string } } };
        setError(e.response?.data?.detail || 'Veri yüklenirken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-red-600 bg-red-50 px-6 py-4 rounded-lg border border-red-200">
          Hata: {error}
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const riskyRestaurantCount = stats.incidents_by_restaurant?.length || 0;
  const daily = stats.daily_breakdown || [];
  const topRest = stats.top_restaurants || [];

  const ordersTrend = calcTrend(daily, 'orders');
  const incidentsTrend = calcTrend(daily, 'incidents');

  const chartData = daily.map((d) => ({
    ...d,
    displayDate: formatDate(d.date),
  }));

  const statsCards = [
    {
      title: 'Toplam Sipariş',
      value: stats.total_orders?.toLocaleString('tr-TR') || '0',
      change: ordersTrend,
      icon: TrendingUp,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Aktif Öğrenci',
      value: stats.total_students?.toLocaleString('tr-TR') || '0',
      change: '—',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Toplam Vaka',
      value: stats.total_incidents?.toLocaleString('tr-TR') || '0',
      change: incidentsTrend,
      icon: AlertCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Riskli Restoran',
      value: riskyRestaurantCount.toString(),
      change: riskyRestaurantCount > 0 ? `${riskyRestaurantCount} adet` : '—',
      icon: UtensilsCrossed,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-700 mt-1">Son 7 günlük özet</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsCards.map((stat) => (
          <Card key={stat.title} className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p
                  className={`text-sm mt-1 ${
                    stat.change.startsWith('+')
                      ? 'text-green-600'
                      : stat.change.startsWith('-')
                        ? 'text-red-600'
                        : 'text-gray-700'
                  }`}
                >
                  {stat.change === '—' ? 'Önceki döneme göre' : stat.change}
                </p>
              </div>
              <div className={`${stat.bgColor} p-3 rounded-full`}>
                <stat.icon className={stat.color} size={24} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Günlük Sipariş & Vaka Trendi
          </h2>
          <div className="h-64">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="displayDate" tick={{ fontSize: 12, fill: '#374151' }} />
                  <YAxis tick={{ fontSize: 12, fill: '#374151' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', color: '#1f2937' }}
                    labelStyle={{ color: '#1f2937', fontWeight: 600 }}
                    formatter={(value: number) => [value]}
                    labelFormatter={(label) => label}
                  />
                  <Legend wrapperStyle={{ color: '#374151' }} />
                  <Line
                    type="monotone"
                    dataKey="orders"
                    name="Sipariş"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="incidents"
                    name="Vaka"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center bg-gray-50 rounded text-gray-500 text-sm">
                Henüz veri yok
              </div>
            )}
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            En Çok Sipariş Verilen Restoranlar
          </h2>
          <div className="h-64">
            {topRest.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={topRest.map((r) => ({
                    name: r.name.length > 18 ? r.name.slice(0, 18) + '...' : r.name,
                    fullName: r.name,
                    count: r.order_count,
                  }))}
                  layout="vertical"
                  margin={{ left: 20, right: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" tick={{ fontSize: 12, fill: '#374151' }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={120}
                    tick={{ fontSize: 11, fill: '#374151' }}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', color: '#1f2937' }}
                    labelStyle={{ color: '#1f2937', fontWeight: 600 }}
                    formatter={(value: number) => [value, 'Sipariş']}
                    labelFormatter={(_, payload) =>
                      (payload?.[0]?.payload?.fullName as string) || ''
                    }
                  />
                  <Bar dataKey="count" name="Sipariş" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center bg-gray-50 rounded text-gray-500 text-sm">
                Henüz veri yok
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
