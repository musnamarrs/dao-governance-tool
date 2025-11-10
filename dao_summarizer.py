"""
DAO Proposal Summarizer - With Pros & Cons Analysis
Can summarize: Latest, All Active, All Closed, or Multiple proposals
"""

import anthropic
import requests
import json
import os
from datetime import datetime

# REPLACE WITH YOUR API KEY
CLAUDE_API_KEY = "input your claude api key"
def fetch_proposals(status="active", limit=10):
    """
    Fetch Arbitrum proposals
    status: "active", "closed", or "all"
    limit: number of proposals to fetch (max 100)
    """
    
    print(f"📡 Fetching {status} proposals (limit: {limit})...")
    
    url = "https://hub.snapshot.org/graphql"
    
    if status == "all":
        where_clause = 'space: "arbitrumfoundation.eth"'
    else:
        where_clause = f'space: "arbitrumfoundation.eth", state: "{status}"'
    
    query = f"""
    query {{
      proposals(
        first: {limit},
        where: {{
          {where_clause}
        }},
        orderBy: "created",
        orderDirection: desc
      ) {{
        id
        title
        body
        choices
        start
        end
        state
        scores_total
      }}
    }}
    """
    
    try:
        response = requests.post(url, json={'query': query})
        data = response.json()
        
        if 'data' in data and 'proposals' in data['data']:
            proposals = data['data']['proposals']
            print(f"✅ Found {len(proposals)} proposals!")
            return proposals
        else:
            print("❌ No proposals found")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def summarize_with_ai(proposal):
    """Use Claude AI to create a detailed summary with pros and cons"""
    
    print(f"\n🤖 Analyzing: {proposal['title'][:50]}...")
    
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    body = proposal['body'][:4000]
    
    prompt = f"""You are a DAO governance expert analyzing proposals for community members who need to make informed voting decisions.

PROPOSAL TITLE: {proposal['title']}

FULL PROPOSAL TEXT:
{body}

VOTING OPTIONS: {proposal['choices']}

Create a comprehensive analysis with BOTH quick reference AND detailed pros/cons:

=== PART 1: EXECUTIVE SUMMARY ===

📊 ONE-LINE SUMMARY (max 15 words)

🎯 WHAT'S PROPOSED (2-3 sentences explaining the main action)

💰 KEY NUMBERS (budget, timeline, affected parties, or metrics if mentioned)

🗳️ VOTING OPTIONS: {proposal['choices']}

=== PART 2: COMMUNITY IMPACT ANALYSIS ===

## ✅ PROS - Benefits for the Community

List 4-6 specific advantages this proposal brings:
- For token holders
- For the DAO treasury/governance
- For developers/builders
- For the broader ecosystem
- For long-term sustainability
- For user experience/adoption

Be specific. Explain HOW each benefit materializes, not just what it is.

## ❌ CONS - Risks & Concerns for the Community

List 4-6 specific risks or downsides:
- Financial risks (cost, opportunity cost, misallocation)
- Governance risks (precedents, centralization, power dynamics)
- Execution risks (complexity, dependencies, timeline)
- Community risks (controversy, division, unintended consequences)
- Strategic risks (long-term positioning, competitive disadvantage)

Be honest and critical. Point out real concerns that voters should consider.

=== PART 3: CRITICAL ANALYSIS ===

## ⚠️ WHAT'S UNCLEAR OR PROBLEMATIC

Identify 3-4 issues that need attention:
- Missing information that should be present
- Vague language that could be exploited
- Contradictions or inconsistencies
- Unrealistic assumptions
- Governance loopholes

## 💡 KEY INSIGHTS

Provide 3-4 deep insights:
- What's the real motivation behind this?
- What precedent does this set?
- Who benefits most? Who might lose?
- What's being overlooked?
- What would an expert think?

## 🎯 THE BOTTOM LINE

In 2-3 sentences: What should delegates consider most carefully when voting?

Write clearly, think critically, and help voters understand both sides of the decision."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        summary = message.content[0].text
        print("   ✅ Analysis complete!")
        return summary
        
    except Exception as e:
        print(f"   ❌ AI Error: {e}")
        return None

def save_summary(proposal, summary, save_dir, index=None):
    """Save individual proposal summary"""
    
    # Create safe filename from proposal title
    safe_title = "".join(c for c in proposal['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title[:50]  # Limit length
    
    if index is not None:
        filename = f"proposal_{index+1:02d}_{safe_title}.txt"
    else:
        filename = f"proposal_{safe_title}.txt"
    
    full_path = os.path.join(save_dir, filename)
    
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write(f"PROPOSAL: {proposal['title']}\n")
            f.write("="*60 + "\n")
            f.write(f"\nSTATUS: {proposal['state'].upper()}\n")
            f.write(f"LINK: https://snapshot.org/#/arbitrumfoundation.eth/proposal/{proposal['id']}\n\n")
            f.write("="*60 + "\n")
            f.write("AI ANALYSIS WITH PROS & CONS\n")
            f.write("="*60 + "\n\n")
            f.write(summary)
            f.write("\n\n" + "="*60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n")
        
        return full_path
    except Exception as e:
        print(f"   ❌ Error saving: {e}")
        return None

def create_index_file(proposals, save_dir, summaries_saved):
    """Create an index file listing all analyzed proposals"""
    
    index_path = os.path.join(save_dir, "00_INDEX.txt")
    
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("ARBITRUM DAO PROPOSALS - PROS & CONS ANALYSIS\n")
            f.write("="*60 + "\n")
            f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Proposals Analyzed: {summaries_saved}\n\n")
            f.write("="*60 + "\n\n")
            
            for i, prop in enumerate(proposals[:summaries_saved], 1):
                f.write(f"{i:02d}. [{prop['state'].upper()}] {prop['title']}\n")
                f.write(f"    Link: https://snapshot.org/#/arbitrumfoundation.eth/proposal/{prop['id']}\n\n")
            
            f.write("="*60 + "\n")
            f.write("Each file contains detailed pros/cons analysis\n")
            f.write("="*60 + "\n")
        
        print(f"\n📋 Index file created: {index_path}")
        return index_path
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        return None

def main():
    """Run the full process"""
    
    print("="*60)
    print("🚀 DAO PROPOSAL SUMMARIZER - PROS & CONS VERSION")
    print("="*60)
    print()
    
    # Setup save directory
    save_dir = "D:\\DAO_Summaries"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"📁 Created directory: {save_dir}")
    else:
        print(f"📁 Save directory: {save_dir}")
    print()
    
    try:
        # Ask user what they want to analyze
        print("What would you like to analyze?")
        print("1. Latest proposal only")
        print("2. All ACTIVE proposals")
        print("3. Last 5 CLOSED proposals")
        print("4. Last 10 proposals (any status)")
        print("5. Custom number of proposals")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        print()
        
        if choice == "1":
            proposals = fetch_proposals("active", 1)
            if not proposals:
                proposals = fetch_proposals("closed", 1)
        elif choice == "2":
            proposals = fetch_proposals("active", 100)
        elif choice == "3":
            proposals = fetch_proposals("closed", 5)
        elif choice == "4":
            proposals = fetch_proposals("all", 10)
        elif choice == "5":
            num = input("How many proposals? (max 100): ").strip()
            try:
                num = int(num)
                num = min(max(1, num), 100)
                proposals = fetch_proposals("all", num)
            except:
                print("Invalid number, fetching 10 proposals")
                proposals = fetch_proposals("all", 10)
        else:
            print("Invalid choice, fetching latest proposal")
            proposals = fetch_proposals("active", 1)
        
        if not proposals:
            print("\n❌ No proposals found")
            print("\nPress ENTER to close...")
            input()
            return
        
        print("\n" + "="*60)
        print(f"📊 ANALYZING {len(proposals)} PROPOSAL(S)")
        print("="*60)
        
        summaries_saved = 0
        saved_paths = []
        
        for i, proposal in enumerate(proposals):
            print(f"\n[{i+1}/{len(proposals)}] Processing: {proposal['title'][:60]}")
            print(f"Status: {proposal['state']} | Link: https://snapshot.org/#/arbitrumfoundation.eth/proposal/{proposal['id']}")
            
            summary = summarize_with_ai(proposal)
            
            if summary:
                path = save_summary(proposal, summary, save_dir, i)
                if path:
                    summaries_saved += 1
                    saved_paths.append(path)
                    print(f"   ✅ Saved to: {os.path.basename(path)}")
            
            # Small delay to avoid rate limits
            if i < len(proposals) - 1:
                import time
                time.sleep(1)
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\n📊 Results:")
        print(f"   - Total proposals: {len(proposals)}")
        print(f"   - Successfully analyzed: {summaries_saved}")
        print(f"   - Failed: {len(proposals) - summaries_saved}")
        
        if summaries_saved > 0:
            # Create index file
            create_index_file(proposals, save_dir, summaries_saved)
            
            print(f"\n📁 All files saved to: {save_dir}")
            print(f"\n🚀 Opening folder...")
            try:
                os.startfile(save_dir)
            except:
                print(f"   Couldn't open folder automatically")
                print(f"   Open manually: {save_dir}")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n" + "="*60)
        print("🎉 PROCESS COMPLETE")
        print("="*60)
        print("\n👉 Press ENTER to close this window...")
        input()

if __name__ == "__main__":
    main()
