import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const API = "http://localhost:8000";
const API_KEY = "bs_test_demo123";

export function useDashboard() {
  const [stats, setStats] = useState({
    total: 0,
    bots: 0,
    humans: 0,
    suspicious: 0,
    catch_rate: 0,
  });
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, feedRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats?api_key=${API_KEY}`),
        axios.get(`${API}/dashboard/feed?api_key=${API_KEY}`),
      ]);
      setStats(statsRes.data);
      setFeed(feedRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Poll every 3 seconds for live updates
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { stats, feed, loading, refresh: fetchData };
}
