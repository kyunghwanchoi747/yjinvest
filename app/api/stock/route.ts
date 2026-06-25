import { NextRequest, NextResponse } from 'next/server';
import yahooFinance from 'yahoo-finance2';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const ticker = searchParams.get('ticker');

    if (!ticker) {
      return NextResponse.json(
        { error: 'ticker parameter is required' },
        { status: 400 }
      );
    }

    // Fetch quote data
    const quote = (await yahooFinance.quote(ticker)) as any;

    // Fetch 1 week historical data
    const historical = (await yahooFinance.historical(ticker, {
      period1: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      period2: new Date(),
      interval: '1d',
    })) as any[];

    // Fetch news
    const searchResults = (await yahooFinance.search(ticker)) as any;
    const news = searchResults.news ? searchResults.news.slice(0, 5) : [];

    const stockData = {
      ticker: quote.symbol,
      shortName: quote.shortName || ticker,
      currentPrice: quote.regularMarketPrice,
      previousClose: quote.regularMarketPreviousClose,
      volume: quote.regularMarketVolume,
      marketCap: quote.marketCap,
      pe: quote.trailingPE,
      fiftyTwoWeekHigh: quote.fiftyTwoWeekHigh,
      fiftyTwoWeekLow: quote.fiftyTwoWeekLow,
      historical: historical.map((day: any) => ({
        date: day.date,
        open: day.open,
        high: day.high,
        low: day.low,
        close: day.close,
        volume: day.volume,
      })),
      news: news.map((item: any) => ({
        title: item.title,
        link: item.link,
        publisher: item.source,
      })),
    };

    return NextResponse.json(stockData);
  } catch (error: any) {
    console.error('Stock API Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch stock data' },
      { status: 500 }
    );
  }
}
