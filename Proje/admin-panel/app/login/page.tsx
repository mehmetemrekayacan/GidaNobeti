/**
 * Login Page - Admin Authentication
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input, Button, Card } from '@/components/ui';
import apiClient from '@/lib/api-client';
import { setToken } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    tckn: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiClient.post('/auth/login', {
        tckn: formData.tckn,
        password: formData.password,
      });

      const { access_token, user } = response.data;

      // Check if user is admin
      if (user.role !== 'DORM_MANAGER' && user.role !== 'SYS_ADMIN') {
        setError('Bu panel sadece yöneticiler içindir.');
        setLoading(false);
        return;
      }

      // Save token
      setToken(access_token);

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(
        err.response?.data?.detail || 
        'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Gıda Nöbeti
          </h1>
          <p className="text-gray-600">Yönetici Paneli</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="TC Kimlik No"
            type="text"
            placeholder="11 haneli TC No"
            value={formData.tckn}
            onChange={(e) => setFormData({ ...formData, tckn: e.target.value })}
            maxLength={11}
            required
          />

          <Input
            label="Şifre"
            type="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            variant="primary"
            className="w-full"
            disabled={loading}
          >
            {loading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Bu sistem yurt yöneticileri içindir.</p>
        </div>
      </Card>
    </div>
  );
}
