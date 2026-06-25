import { NextRequest, NextResponse } from 'next/server';

// Fetch real-time exchange rate from exchangerate-api.com
const getExchangeRate = async (): Promise<number> => {
  try {
    const res = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
    if (!res.ok) throw new Error('Failed to fetch exchange rate');
    const data = await res.json();
    return Math.round(data.rates.KRW * 100) / 100; // KRW/USD
  } catch (error) {
    console.error('Exchange rate API error:', error);
    return 1315; // Fallback value
  }
};

const getMacroData = async () => {
  const exchangeRate = await getExchangeRate();

  return {
    korea_base_rate: 3.25,
    korea_base_rate_source: '한국은행 기준금리 (2026년 기준)',
    us_base_rate: 4.5,
    exchange_rate: exchangeRate,
    cpi_inflation: 2.1,
    korea_base_rate_history: {
      dates: [
        '2024-01',
        '2024-02',
        '2024-03',
        '2024-04',
        '2024-05',
        '2024-06',
      ],
      rates: [3.5, 3.5, 3.5, 3.5, 3.5, 3.25],
    },
  };
};

export async function GET(req: NextRequest) {
  try {
    const macroData = await getMacroData();
    return NextResponse.json(macroData);
  } catch (error: any) {
    console.error('Macro API Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch macro data' },
      { status: 500 }
    );
  }
}
