export interface Page<T> { items: T[]; total: number; limit: number; offset: number }
export interface Tender { id: string; external_id?: string; title: string; description?: string; status: string }
export class OpenProcurementHubClient {
  constructor(private readonly baseUrl: string, private readonly apiKey?: string) {}
  async tenders(limit = 50, offset = 0): Promise<Page<Tender>> {
    const res = await fetch(`${this.baseUrl.replace(/\/$/, '')}/api/v1/tenders?limit=${limit}&offset=${offset}`, {headers: this.apiKey ? {Authorization: `Bearer ${this.apiKey}`} : {}});
    if (!res.ok) throw new Error(`OpenProcurementHub request failed: ${res.status}`);
    return res.json() as Promise<Page<Tender>>;
  }
}
