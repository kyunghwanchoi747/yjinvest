import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

export async function POST(req: NextRequest) {
  try {
    const apiKey = process.env.GOOGLE_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: 'GOOGLE_API_KEY is not configured' },
        { status: 400 }
      );
    }

    const { stockData, macroData } = await req.json();

    if (!stockData) {
      return NextResponse.json(
        { error: 'stockData is required' },
        { status: 400 }
      );
    }

    const client = new GoogleGenerativeAI(apiKey);
    const model = client.getGenerativeModel({ model: 'gemini-2.0-flash' });

    const prompt = `You are a professional stock analyst. Analyze the following stock and macro economic data, and provide comprehensive investment insights in Korean.

**Stock Data:**
- Company: ${stockData.shortName} (${stockData.ticker})
- Current Price: ${stockData.currentPrice}
- Previous Close: ${stockData.previousClose}
- Volume: ${stockData.volume}
- Market Cap: ${stockData.marketCap}
- P/E Ratio: ${stockData.pe}
- 52 Week High: ${stockData.fiftyTwoWeekHigh}
- 52 Week Low: ${stockData.fiftyTwoWeekLow}

**Macro Economic Data:**
- Korea Base Rate: ${macroData.korea_base_rate}%
- US Base Rate: ${macroData.us_base_rate}%
- Exchange Rate (KRW/USD): ${macroData.exchange_rate}
- CPI Inflation: ${macroData.cpi_inflation}%

Please provide:
1. Current market sentiment and price analysis
2. Macro economic factors impact
3. Investment recommendation (Buy/Hold/Sell)
4. Risk assessment
5. 3-6 month price target

Keep response concise and professional.`;

    const result = await model.generateContent(prompt);
    const insight = result.response.text();

    return NextResponse.json({ insight });
  } catch (error: any) {
    console.error('Analysis API Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to generate analysis' },
      { status: 500 }
    );
  }
}
