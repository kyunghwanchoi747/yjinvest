import { NextRequest, NextResponse } from 'next/server';

// Mock macro economic data - replace with actual ECOS API integration
const getMacroData = async () => {
  return {
    korea_base_rate: 3.25,
    korea_base_rate_source: '한국은행 기준금리 (2024년 기준)',
    us_base_rate: 4.5,
    exchange_rate: 1180,
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
