import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../services/api';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats().then(r => r.data),
  });

  if (isLoading) {
    return <div className="text-center py-12">Загрузка...</div>;
  }

  const statCards = [
    { title: 'Заказов сегодня', value: stats?.total_orders_today || 0, color: 'bg-blue-500' },
    { title: 'Выручка сегодня', value: `${stats?.total_revenue_today || 0} ₽`, color: 'bg-green-500' },
    { title: 'В ожидании', value: stats?.pending_orders || 0, color: 'bg-yellow-500' },
    { title: 'Активные доставки', value: stats?.active_deliveries || 0, color: 'bg-purple-500' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card) => (
          <div key={card.title} className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{card.value}</p>
              </div>
              <div className={`w-12 h-12 ${card.color} rounded-lg opacity-20`}></div>
            </div>
          </div>
        ))}
      </div>

      {/* Popular Products */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Популярные товары</h2>
        {stats?.popular_products && stats.popular_products.length > 0 ? (
          <div className="space-y-3">
            {stats.popular_products.map((product, index) => (
              <div key={product.product_id} className="flex items-center justify-between py-3 border-b last:border-0">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center justify-center w-8 h-8 bg-primary-100 text-primary-700 rounded-full font-medium">
                    {index + 1}
                  </span>
                  <span className="font-medium text-gray-900">{product.product_name}</span>
                </div>
                <span className="text-gray-600">{product.orders_count} заказов</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">Нет данных</p>
        )}
      </div>

      <p className="text-sm text-gray-500 mt-4">
        Обновлено: {format(new Date(), 'dd MMMM yyyy, HH:mm', { locale: ru })}
      </p>
    </div>
  );
}
