"""
Airtable Integration
====================

Manages the topic queue database in Airtable.

Usage:
    from integrations.airtable import TopicQueue
    
    queue = TopicQueue()
    topics = queue.get_pending_topics()
    queue.update_status(topic_id, "researched")
"""

import os
import requests
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Topic:
    """A topic from the queue"""
    id: str
    title: str
    url: str
    source: str
    score: int
    reasoning: str
    angles: list[str]
    status: str
    research_brief: Optional[str] = None
    created_at: Optional[str] = None
    approved_by: Optional[str] = None
    
    @property
    def is_approved(self) -> bool:
        return self.status in ["approved", "pending"] and self.score >= 7


class AirtableClient:
    """
    Base client for Airtable API.
    
    Uses the official Airtable REST API.
    """
    
    BASE_URL = "https://api.airtable.com/v0"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_id: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("AIRTABLE_API_KEY")
        self.base_id = base_id or os.getenv("AIRTABLE_BASE_ID")
        
        if not self.api_key:
            raise ValueError(
                "Airtable API key required. Set AIRTABLE_API_KEY env var "
                "or pass api_key parameter."
            )
        if not self.base_id:
            raise ValueError(
                "Airtable base ID required. Set AIRTABLE_BASE_ID env var "
                "or pass base_id parameter."
            )
    
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _url(self, table: str, record_id: str = None) -> str:
        url = f"{self.BASE_URL}/{self.base_id}/{table}"
        if record_id:
            url += f"/{record_id}"
        return url
    
    def list_records(
        self,
        table: str,
        filter_formula: str = None,
        max_records: int = 100,
        sort: list[dict] = None
    ) -> list[dict]:
        """List records from a table with optional filtering"""
        
        params = {"maxRecords": max_records}
        
        if filter_formula:
            params["filterByFormula"] = filter_formula
        
        if sort:
            for i, s in enumerate(sort):
                params[f"sort[{i}][field]"] = s["field"]
                params[f"sort[{i}][direction]"] = s.get("direction", "asc")
        
        response = requests.get(
            self._url(table),
            headers=self._headers(),
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Airtable error: {response.status_code} - {response.text}")
        
        return response.json().get("records", [])
    
    def get_record(self, table: str, record_id: str) -> dict:
        """Get a single record by ID"""
        
        response = requests.get(
            self._url(table, record_id),
            headers=self._headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Airtable error: {response.status_code}")
        
        return response.json()
    
    def create_record(self, table: str, fields: dict) -> dict:
        """Create a new record"""
        
        response = requests.post(
            self._url(table),
            headers=self._headers(),
            json={"fields": fields},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Airtable error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def update_record(self, table: str, record_id: str, fields: dict) -> dict:
        """Update an existing record"""
        
        response = requests.patch(
            self._url(table, record_id),
            headers=self._headers(),
            json={"fields": fields},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Airtable error: {response.status_code}")
        
        return response.json()
    
    def delete_record(self, table: str, record_id: str) -> bool:
        """Delete a record"""
        
        response = requests.delete(
            self._url(table, record_id),
            headers=self._headers(),
            timeout=30
        )
        
        return response.status_code == 200


class TopicQueue(AirtableClient):
    """
    Manages the video topic queue in Airtable.
    
    Expected table schema:
    - Title (text)
    - URL (url)
    - Source (single select)
    - Score (number)
    - Reasoning (long text)
    - Angles (long text, JSON)
    - Status (single select: pending, approved, rejected, researched, scripted, produced)
    - Research Brief (long text)
    - Created At (datetime)
    - Approved By (collaborator)
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_id: str = None,
        table_name: str = None
    ):
        super().__init__(api_key, base_id)
        self.table = table_name or os.getenv("AIRTABLE_TABLE_NAME", "Topic Queue")
    
    def _record_to_topic(self, record: dict) -> Topic:
        """Convert Airtable record to Topic object"""
        fields = record.get("fields", {})
        
        # Parse angles from JSON string
        angles_raw = fields.get("Angles", "[]")
        try:
            import json
            angles = json.loads(angles_raw) if isinstance(angles_raw, str) else angles_raw
        except:
            angles = []
        
        return Topic(
            id=record["id"],
            title=fields.get("Title", ""),
            url=fields.get("URL", ""),
            source=fields.get("Source", ""),
            score=fields.get("Score", 0),
            reasoning=fields.get("Reasoning", ""),
            angles=angles if isinstance(angles, list) else [angles],
            status=fields.get("Status", "pending"),
            research_brief=fields.get("Research Brief"),
            created_at=fields.get("Created At"),
            approved_by=fields.get("Approved By")
        )
    
    def get_pending_topics(self) -> list[Topic]:
        """Get all topics pending approval"""
        
        records = self.list_records(
            self.table,
            filter_formula="{Status} = 'pending'",
            sort=[{"field": "Score", "direction": "desc"}]
        )
        
        return [self._record_to_topic(r) for r in records]
    
    def get_approved_topics(self) -> list[Topic]:
        """Get all approved topics ready for production"""
        
        records = self.list_records(
            self.table,
            filter_formula="{Status} = 'approved'",
            sort=[{"field": "Created At", "direction": "asc"}]
        )
        
        return [self._record_to_topic(r) for r in records]
    
    def get_topic(self, topic_id: str) -> Topic:
        """Get a specific topic by ID"""
        record = self.get_record(self.table, topic_id)
        return self._record_to_topic(record)
    
    def add_topic(
        self,
        title: str,
        url: str,
        source: str,
        score: int,
        reasoning: str,
        angles: list[str],
        risk_factors: list[str] = None
    ) -> Topic:
        """Add a new topic to the queue"""
        import json
        
        fields = {
            "Title": title,
            "URL": url,
            "Source": source,
            "Score": score,
            "Reasoning": reasoning,
            "Angles": json.dumps(angles),
            "Risk Factors": json.dumps(risk_factors or []),
            "Status": "pending"
        }
        
        record = self.create_record(self.table, fields)
        return self._record_to_topic(record)
    
    def update_status(self, topic_id: str, status: str) -> Topic:
        """Update topic status"""
        
        valid_statuses = ["pending", "approved", "rejected", "researched", "scripted", "produced"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        record = self.update_record(self.table, topic_id, {"Status": status})
        return self._record_to_topic(record)
    
    def approve_topic(self, topic_id: str) -> Topic:
        """Approve a topic for production"""
        return self.update_status(topic_id, "approved")
    
    def reject_topic(self, topic_id: str) -> Topic:
        """Reject a topic"""
        return self.update_status(topic_id, "rejected")
    
    def save_research_brief(self, topic_id: str, brief: str) -> Topic:
        """Save research brief and update status"""
        
        record = self.update_record(
            self.table,
            topic_id,
            {
                "Research Brief": brief,
                "Status": "researched"
            }
        )
        return self._record_to_topic(record)
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        
        all_records = self.list_records(self.table, max_records=1000)
        
        stats = {
            "total": len(all_records),
            "by_status": {},
            "avg_score": 0,
            "high_score_count": 0
        }
        
        scores = []
        for record in all_records:
            fields = record.get("fields", {})
            status = fields.get("Status", "unknown")
            score = fields.get("Score", 0)
            
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            scores.append(score)
            
            if score >= 7:
                stats["high_score_count"] += 1
        
        if scores:
            stats["avg_score"] = sum(scores) / len(scores)
        
        return stats


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  List pending: python airtable.py pending")
        print("  List approved: python airtable.py approved")
        print("  Get stats: python airtable.py stats")
        print("  Approve topic: python airtable.py approve <record_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        queue = TopicQueue()
        
        if command == "pending":
            topics = queue.get_pending_topics()
            print(f"Pending topics ({len(topics)}):\n")
            for t in topics:
                print(f"  [{t.score}/10] {t.title[:50]}...")
                print(f"    ID: {t.id}")
                print(f"    Source: {t.source}")
                print()
        
        elif command == "approved":
            topics = queue.get_approved_topics()
            print(f"Approved topics ({len(topics)}):\n")
            for t in topics:
                print(f"  [{t.score}/10] {t.title[:50]}...")
                print(f"    ID: {t.id}")
                print(f"    Angles: {len(t.angles)} available")
                print()
        
        elif command == "stats":
            stats = queue.get_stats()
            print(f"Queue Statistics:")
            print(f"  Total topics: {stats['total']}")
            print(f"  Average score: {stats['avg_score']:.1f}")
            print(f"  High scorers (≥7): {stats['high_score_count']}")
            print(f"\n  By status:")
            for status, count in stats["by_status"].items():
                print(f"    {status}: {count}")
        
        elif command == "approve" and len(sys.argv) >= 3:
            topic_id = sys.argv[2]
            topic = queue.approve_topic(topic_id)
            print(f"✅ Approved: {topic.title}")
        
        else:
            print("Invalid command")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("\nSet environment variables:")
        print("  $env:AIRTABLE_API_KEY = 'your_key'")
        print("  $env:AIRTABLE_BASE_ID = 'your_base_id'")
