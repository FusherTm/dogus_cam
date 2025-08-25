import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { dashboardSummarySchema, DashboardSummary } from '../types/dashboard'

const Dashboard = () => {
  const { data, isLoading, error } = useQuery<DashboardSummary>({
    queryKey: ['dashboardSummary'],
    queryFn: async () => {
      const res = await api.get('/dashboard/summary')
      return dashboardSummarySchema.parse(res.data)
    },
  })

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>Error loading summary</p>

  return (
    <div style={{ padding: '1rem', flex: 1 }}>
      <h1>Dashboard</h1>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <div style={{ border: '1px solid #ccc', padding: '1rem' }}>
          <strong>Bugün satış</strong>
          <div>{data!.salesToday}</div>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '1rem' }}>
          <strong>Bu ay satış</strong>
          <div>{data!.salesThisMonth}</div>
        </div>
      </div>

      <h2 style={{ marginTop: '1rem' }}>Açık Alacaklar</h2>
      <div>{data!.receivablesTotal}</div>
      <ul>
        {data!.receivablesAging.map((a) => (
          <li key={a.period}>
            {a.period}: {a.amount}
          </li>
        ))}
      </ul>

      <h2>Düşük Stok</h2>
      <table border={1} cellPadding={4} style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Ad</th>
            <th>Total</th>
            <th>Restock Level</th>
          </tr>
        </thead>
        <tbody>
          {data!.lowStock.map((item) => (
            <tr key={item.sku}>
              <td>{item.sku}</td>
              <td>{item.name}</td>
              <td>{item.total}</td>
              <td>{item.restock_level}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>En iyi müşteriler</h2>
      <table border={1} cellPadding={4} style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>Ad</th>
            <th>Toplam</th>
          </tr>
        </thead>
        <tbody>
          {data!.topCustomers.map((c, idx) => (
            <tr key={idx}>
              <td>{c.name}</td>
              <td>{c.total}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Dashboard
