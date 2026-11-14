"use client";

import { useState, useEffect } from "react";
import { MapPin, Star, MessageSquare, Eye, Phone, Navigation, PenSquare, Send, RefreshCw } from "lucide-react";
import { useAuth } from "@/context/auth";

interface GMBProfile {
  business_name: string;
  address: string;
  phone: string;
  rating: number;
  review_count: number;
  verified: boolean;
  hours: Record<string, string>;
  demo_mode?: boolean;
}

interface GMBReview {
  id: string;
  reviewer: string;
  rating: number;
  text: string;
  time: string;
  replied: boolean;
}

interface GMBInsights {
  profile_views: number;
  search_appearances: number;
  direction_requests: number;
  phone_calls: number;
  website_clicks: number;
  photo_views: number;
  demo_mode?: boolean;
}

export default function GoogleBusinessPage() {
  const { token } = useAuth();
  const [profile, setProfile] = useState<GMBProfile | null>(null);
  const [reviews, setReviews] = useState<GMBReview[]>([]);
  const [insights, setInsights] = useState<GMBInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "reviews" | "posts">("overview");

  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (!token) return;
    fetchData();
  }, [token]);

  async function fetchData() {
    setLoading(true);
    const headers = { Authorization: `Bearer ${token}` };
    try {
      const [profileRes, reviewsRes, insightsRes] = await Promise.all([
        fetch(`${API}/api/v1/gmb/profile`, { headers }),
        fetch(`${API}/api/v1/gmb/reviews`, { headers }),
        fetch(`${API}/api/v1/gmb/insights`, { headers }),
      ]);
      if (profileRes.ok) setProfile(await profileRes.json());
      if (reviewsRes.ok) setReviews((await reviewsRes.json()).reviews || []);
      if (insightsRes.ok) setInsights(await insightsRes.json());
    } catch (err) {
      console.error("GMB fetch error:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Google Business Profile</h1>
          <p className="text-sm text-slate-500 mt-1">Manage your clinic&apos;s presence on Google Maps &amp; Search</p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition text-sm font-medium"
        >
          <RefreshCw className="w-4 h-4" /> Sync Profile
        </button>
      </div>

      {profile?.demo_mode && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
          <strong>Demo Mode:</strong> Connect your Google My Business account in Settings to see real data.
        </div>
      )}

      {/* Profile Card */}
      {profile && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
              <MapPin className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-slate-900">{profile.business_name}</h2>
                {profile.verified && (
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">Verified</span>
                )}
              </div>
              <p className="text-sm text-slate-500 mt-0.5">{profile.address}</p>
              <div className="flex items-center gap-4 mt-2">
                <span className="flex items-center gap-1 text-sm">
                  <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                  <strong>{profile.rating}</strong>
                  <span className="text-slate-500">({profile.review_count} reviews)</span>
                </span>
                <span className="text-sm text-slate-500">{profile.phone}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Insights Cards */}
      {insights && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { label: "Profile Views", value: insights.profile_views, icon: Eye, color: "blue" },
            { label: "Search Appearances", value: insights.search_appearances, icon: MapPin, color: "emerald" },
            { label: "Direction Requests", value: insights.direction_requests, icon: Navigation, color: "purple" },
            { label: "Phone Calls", value: insights.phone_calls, icon: Phone, color: "orange" },
            { label: "Website Clicks", value: insights.website_clicks || 0, icon: Eye, color: "sky" },
            { label: "Photo Views", value: insights.photo_views, icon: Eye, color: "pink" },
          ].map((stat) => (
            <div key={stat.label} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500 mb-1">{stat.label}</div>
              <div className="text-xl font-bold text-slate-900">{stat.value.toLocaleString()}</div>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 rounded-lg p-1 w-fit">
        {(["overview", "reviews", "posts"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              activeTab === tab ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Reviews Tab */}
      {activeTab === "reviews" && (
        <div className="space-y-3">
          {reviews.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500">
              No reviews yet. Share your review link with patients to get started.
            </div>
          ) : (
            reviews.map((review) => (
              <div key={review.id} className="bg-white rounded-xl border border-slate-200 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-900">{review.reviewer}</span>
                    <div className="flex">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3.5 h-3.5 ${i < review.rating ? "text-amber-500 fill-amber-500" : "text-slate-300"}`}
                        />
                      ))}
                    </div>
                  </div>
                  <span className="text-xs text-slate-400">{review.time}</span>
                </div>
                <p className="text-sm text-slate-700">{review.text}</p>
                {!review.replied && (
                  <button className="mt-2 text-xs text-emerald-600 hover:text-emerald-700 font-medium flex items-center gap-1">
                    <MessageSquare className="w-3 h-3" /> AI Generate Reply
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Posts Tab */}
      {activeTab === "posts" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-4">Create Google Business Post</h3>
          <div className="space-y-3">
            <div>
              <label className="text-sm text-slate-600 block mb-1">Post Type</label>
              <select className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm">
                <option value="UPDATE">Update</option>
                <option value="OFFER">Offer / Promotion</option>
                <option value="EVENT">Event</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-slate-600 block mb-1">Content</label>
              <textarea
                rows={3}
                placeholder="Write your post or click AI Generate..."
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm resize-none"
              />
            </div>
            <div className="flex gap-2">
              <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium">
                <PenSquare className="w-4 h-4" /> AI Generate
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition text-sm font-medium">
                <Send className="w-4 h-4" /> Publish
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-slate-50 border border-slate-200 text-sm flex items-center gap-3">
                <MessageSquare className="w-4 h-4 text-emerald-600" />
                Get Review Request Link
              </button>
              <button className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-slate-50 border border-slate-200 text-sm flex items-center gap-3">
                <PenSquare className="w-4 h-4 text-purple-600" />
                Create New Post
              </button>
              <button className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-slate-50 border border-slate-200 text-sm flex items-center gap-3">
                <RefreshCw className="w-4 h-4 text-blue-600" />
                Sync Profile from Google
              </button>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-3">Review Summary</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Total Reviews</span>
                <span className="font-medium">{profile?.review_count || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Average Rating</span>
                <span className="font-medium flex items-center gap-1">
                  <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                  {profile?.rating || 0}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Unreplied Reviews</span>
                <span className="font-medium text-amber-600">{reviews.filter(r => !r.replied).length}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
