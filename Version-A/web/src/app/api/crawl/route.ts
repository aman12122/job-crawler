import { NextResponse } from 'next/server';

export async function POST() {
  const scraperUrl = process.env.SCRAPER_URL;

  if (!scraperUrl) {
    return NextResponse.json({ error: 'Scraper URL not configured' }, { status: 500 });
  }

  try {
    const response = await fetch(`${scraperUrl}/crawl`, {
      method: 'POST',
    });

    if (response.status === 202) {
      return NextResponse.json({ message: 'Crawl started' }, { status: 202 });
    } else if (response.status === 409) {
      return NextResponse.json({ message: 'Crawl already in progress' }, { status: 409 });
    } else {
      return NextResponse.json({ error: 'Failed to trigger crawl' }, { status: 500 });
    }
  } catch (error) {
    console.error('Error triggering crawl:', error);
    return NextResponse.json({ error: 'Failed to communicate with scraper' }, { status: 500 });
  }
}
