"""
Delhi Digital Twin - Crisis Scenario Demo
Hackathon Presentation Script
"""

import time
import json
from datetime import datetime

class CrisisScenarioDemo:
    """
    Simulates a real pollution crisis for hackathon demo
    Timeline: November 5, 2024 - Peak stubble burning season
    """
    
    def __init__(self):
        self.scenario_name = "Diwali + Stubble Burning Crisis"
        self.date = "November 5, 2024"
        self.start_time = "6:00 AM"
        
    def act_1_crisis_develops(self):
        """Act 1: Crisis Develops (30 seconds)"""
        print("\n" + "="*60)
        print("ACT 1: CRISIS DEVELOPS")
        print("="*60)
        
        timeline = [
            {
                "time": "4:00 AM",
                "event": "NASA satellites detect 3,000+ farm fires in Punjab",
                "aqi": {"zone_1": 250, "zone_2": 230, "zone_3": 270, "zone_4": 280, "zone_5": 260}
            },
            {
                "time": "5:00 AM", 
                "event": "Northwest winds (15 km/h) carrying smoke to Delhi",
                "aqi": {"zone_1": 320, "zone_2": 310, "zone_3": 350, "zone_4": 380, "zone_5": 340}
            },
            {
                "time": "6:00 AM",
                "event": "🚨 CRITICAL: Rohini AQI crosses 400 - HAZARDOUS",
                "aqi": {"zone_1": 380, "zone_2": 370, "zone_3": 410, "zone_4": 450, "zone_5": 390}
            }
        ]
        
        for event in timeline:
            print(f"\n⏰ {event['time']}")
            print(f"📍 {event['event']}")
            print(f"📊 AQI Levels: {json.dumps(event['aqi'], indent=2)}")
            time.sleep(2)
        
        return timeline[-1]['aqi']
    
    def act_2_ai_analysis(self, current_aqi):
        """Act 2: AI Analysis (20 seconds)"""
        print("\n" + "="*60)
        print("ACT 2: AI ANALYZES SITUATION")
        print("="*60)
        
        analysis = {
            "severity": "CRITICAL",
            "crisis_zones": [3, 4],  # Dwarka and Rohini
            "affected_population": 2500000,
            "vulnerable_groups": {
                "school_children": 180000,
                "elderly": 95000,
                "outdoor_workers": 65000
            },
            "primary_source": "stubble_burning (40%) + vehicular (35%)",
            "weather_impact": "Temperature inversion trapping pollutants",
            "predicted_peak": "8:00 AM - 10:00 AM (rush hour)"
        }
        
        print("\n🤖 AI SITUATIONAL ANALYSIS:")
        for key, value in analysis.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
            time.sleep(1)
        
        # Calculate health impact
        print("\n⚠️ HEALTH IMPACT PREDICTION:")
        print(f"  • Respiratory emergencies: +300% in next 6 hours")
        print(f"  • Lives at risk today: 45")
        print(f"  • Economic loss if no action: ₹50 crores")
        
        return analysis
    
    def act_3_ai_recommendations(self, analysis):
        """Act 3: AI Generates Solutions (30 seconds)"""
        print("\n" + "="*60)
        print("ACT 3: AI RECOMMENDS INTERVENTIONS")
        print("="*60)
        
        recommendations = [
            {
                "priority": 1,
                "name": "EMERGENCY PROTOCOL ALPHA",
                "description": "Immediate comprehensive response",
                "actions": [
                    "🚛 Ban all trucks on Ring Road (6 AM - 6 PM)",
                    "🏫 Close schools in zones 3 & 4",
                    "🏗️ Halt all construction activities",
                    "🚇 Free metro for 24 hours"
                ],
                "impact": {
                    "aqi_reduction": 120,
                    "implementation_time": "30 minutes",
                    "lives_saved": 35,
                    "confidence": "95%"
                }
            },
            {
                "priority": 2,
                "name": "TRAFFIC OPTIMIZATION",
                "description": "AI-optimized traffic management",
                "actions": [
                    "🚦 Adaptive signal timing on 50 intersections",
                    "🚗 Odd-even enforcement via ANPR cameras",
                    "🚌 Deploy 200 extra buses on key routes",
                    "📱 Push notifications for route alternatives"
                ],
                "impact": {
                    "aqi_reduction": 65,
                    "implementation_time": "2 hours",
                    "lives_saved": 18,
                    "confidence": "88%"
                }
            },
            {
                "priority": 3,
                "name": "EXPOSURE MANAGEMENT",
                "description": "Protect vulnerable populations",
                "actions": [
                    "👴 Door-to-door N95 distribution in hotspots",
                    "🏥 Mobile medical units deployed",
                    "📢 SMS alerts to 10 million citizens",
                    "🌬️ Activate all smog towers and misting systems"
                ],
                "impact": {
                    "aqi_reduction": 25,
                    "implementation_time": "1 hour",
                    "lives_saved": 12,
                    "confidence": "92%"
                }
            }
        ]
        
        for rec in recommendations:
            print(f"\n{'🔴' if rec['priority'] == 1 else '🟡' if rec['priority'] == 2 else '🔵'} PRIORITY {rec['priority']}: {rec['name']}")
            print(f"   {rec['description']}")
            print("\n   Actions:")
            for action in rec['actions']:
                print(f"   {action}")
                time.sleep(0.5)
            print(f"\n   Expected Impact:")
            print(f"   • AQI Reduction: {rec['impact']['aqi_reduction']} points")
            print(f"   • Lives Saved: {rec['impact']['lives_saved']}")
            print(f"   • Implementation: {rec['impact']['implementation_time']}")
            print(f"   • Confidence: {rec['impact']['confidence']}")
            time.sleep(2)
        
        return recommendations[0]  # Return top recommendation
    
    def act_4_virtual_testing(self, intervention):
        """Act 4: Virtual Testing (20 seconds)"""
        print("\n" + "="*60)
        print("ACT 4: VIRTUAL TESTING (No Public Disruption)")
        print("="*60)
        
        print("\n🔬 RUNNING SIMULATION...")
        time.sleep(2)
        
        # Simulate hour-by-hour impact
        simulation_results = [
            {"hour": "7:00 AM", "aqi": 450, "status": "Intervention begins"},
            {"hour": "8:00 AM", "aqi": 410, "status": "Trucks diverted, traffic flowing"},
            {"hour": "9:00 AM", "aqi": 380, "status": "Schools closed, reduced exposure"},
            {"hour": "10:00 AM", "aqi": 350, "status": "Free metro reducing car usage"},
            {"hour": "12:00 PM", "aqi": 330, "status": "AQI dropping steadily"},
            {"hour": "2:00 PM", "aqi": 310, "status": "Target achieved - 120 point reduction"}
        ]
        
        for result in simulation_results:
            print(f"\n⏰ {result['hour']}: AQI = {result['aqi']} | {result['status']}")
            # Show visual progress bar
            progress = int((450 - result['aqi']) / 120 * 20)
            bar = "█" * progress + "░" * (20 - progress)
            print(f"   Progress: [{bar}] {int((450 - result['aqi']) / 120 * 100)}%")
            time.sleep(1.5)
        
        print("\n✅ SIMULATION COMPLETE")
        print("   • Total AQI Reduction: 120 points")
        print("   • Lives Saved: 35")
        print("   • No actual disruption during testing")
        
        return simulation_results
    
    def act_5_implementation(self, simulation_results):
        """Act 5: Real Implementation (20 seconds)"""
        print("\n" + "="*60)
        print("ACT 5: IMPLEMENTATION & RESULTS")
        print("="*60)
        
        print("\n📱 NOTIFICATIONS SENT:")
        notifications = [
            "✉️ SMS sent to 10 million citizens",
            "📲 Push notifications via Delhi Gov app",
            "📺 Emergency broadcast on TV/Radio",
            "🚨 Google Maps updated with restrictions"
        ]
        
        for notif in notifications:
            print(f"   {notif}")
            time.sleep(0.5)
        
        print("\n🎯 REAL-WORLD RESULTS (12 hours later):")
        results = {
            "AQI Reduction": "Achieved 125 points (5 more than predicted)",
            "Lives Saved": "37 (emergency admissions down 70%)",
            "Compliance Rate": "94% (via CCTV monitoring)",
            "Public Sentiment": "82% positive (Twitter sentiment analysis)",
            "Economic Impact": "₹12 crores saved in healthcare costs"
        }
        
        for key, value in results.items():
            print(f"   • {key}: {value}")
            time.sleep(1)
        
        return results
    
    def run_complete_demo(self):
        """Run the complete crisis scenario demo"""
        print("\n" + "🌟"*30)
        print("DELHI DIGITAL TWIN - CRISIS RESPONSE DEMO")
        print(f"Scenario: {self.scenario_name}")
        print(f"Date: {self.date}")
        print("🌟"*30)
        
        input("\nPress Enter to begin the demo...")
        
        # Act 1: Crisis develops
        current_aqi = self.act_1_crisis_develops()
        input("\n➡️ Press Enter to continue to AI Analysis...")
        
        # Act 2: AI analyzes
        analysis = self.act_2_ai_analysis(current_aqi)
        input("\n➡️ Press Enter to see AI Recommendations...")
        
        # Act 3: AI recommends
        top_intervention = self.act_3_ai_recommendations(analysis)
        input("\n➡️ Press Enter to run Virtual Testing...")
        
        # Act 4: Virtual testing
        simulation = self.act_4_virtual_testing(top_intervention)
        input("\n➡️ Press Enter to see Implementation Results...")
        
        # Act 5: Implementation
        results = self.act_5_implementation(simulation)
        
        # Final summary
        print("\n" + "🏆"*30)
        print("MISSION ACCOMPLISHED")
        print("🏆"*30)
        print(f"\n✅ Crisis resolved in 12 hours")
        print(f"✅ 37 lives saved")
        print(f"✅ ₹12 crores in healthcare costs avoided")
        print(f"✅ No trial-and-error, got it right first time")
        print(f"\n💡 This is the power of AI-driven policy testing!")
        print(f"💡 Delhi Digital Twin - Turning data into saved lives.")

if __name__ == "__main__":
    demo = CrisisScenarioDemo()
    demo.run_complete_demo()
