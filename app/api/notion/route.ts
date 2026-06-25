import { NextRequest, NextResponse } from 'next/server';
import { Client } from '@notionhq/client';

export async function POST(req: NextRequest) {
  try {
    const { ticker, price, summary, note } = await req.json();

    const token = process.env.NOTION_TOKEN;
    const databaseId = process.env.NOTION_DB_ID;

    if (!token || !databaseId) {
      return NextResponse.json(
        { error: 'Notion credentials are not configured' },
        { status: 400 }
      );
    }

    if (!ticker || !price) {
      return NextResponse.json(
        { error: 'ticker and price are required' },
        { status: 400 }
      );
    }

    const notion = new Client({ auth: token });

    const finalSummary = note ? `${summary}\n\n[투자자 노트]: ${note}` : summary;

    const response = await notion.pages.create({
      parent: { database_id: databaseId },
      properties: {
        // Adjust these properties based on your Notion database structure
        Name: {
          title: [
            {
              text: {
                content: ticker,
              },
            },
          ],
        },
        Price: {
          number: price,
        },
        Summary: {
          rich_text: [
            {
              text: {
                content: finalSummary.substring(0, 2000), // Notion limit
              },
            },
          ],
        },
        Date: {
          date: {
            start: new Date().toISOString().split('T')[0],
          },
        },
        Status: {
          status: {
            name: 'Analyzed',
          },
        },
      },
    });

    return NextResponse.json({
      success: true,
      pageId: response.id,
    });
  } catch (error: any) {
    console.error('Notion API Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to save to Notion' },
      { status: 500 }
    );
  }
}
