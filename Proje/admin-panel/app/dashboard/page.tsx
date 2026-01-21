/**
 * Dashboard Page - Statistics & Charts
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui';
import { isAuthenticated } from '@/lib/auth';
import { TrendingUp, Users, AlertCircle, UtensilsCrossed } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    if (!isAuthenticated()) {
      router.push('/login');
    } else {
      setLoading(false);
    }
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Yükleniyor...</div>
      </div>
    );
  }

  // Mock data - Backend bağlandığında gerçek data gelecek
  const stats = [
    {
      title: 'Toplam Sipariş',
      value: '1,234',
      change: '+12%',
      icon: TrendingUp,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Aktif Öğrenci',
      value: '456',
      change: '+5%',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Toplam Vaka',
      value: '23',
      change: '-8%',
      icon: AlertCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Riskli Restoran',
      value: '7',
      change: '+2',
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
        {stats.map((stat) => (
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
