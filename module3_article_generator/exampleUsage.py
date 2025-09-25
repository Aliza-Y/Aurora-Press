import os
from dotenv import load_dotenv
from agenticArticleGen import ArticleGenerationWorkflow
import json

# Load environment variables explicitly at the beginning
load_dotenv()
print("🔧 Environment Check:")
print(f"GROQ_API_KEY environment variable is {'set' if os.environ.get('GROQ_API_KEY') else 'NOT set'}")
print(f"GROQ_API_URL environment variable is {'set' if os.environ.get('GROQ_API_URL') else 'NOT set (using default)'}")
print(f"GROQ_MODEL environment variable is {'set' if os.environ.get('GROQ_MODEL') else 'NOT set (using default)'}")
print("-" * 50)

# Example input from News Crawler Agent
crawler_data = {
    "title": "Pakistan India War",
    "keywords": [
        "Pakistan", "India", "Pahalgam Attack", "Pak-India war"
    ],
    "summary": "On April 22, 2025, tensions flared between India and Pakistan after a terror attack in Pahalgam (Jammu and Kashmir) killed 26 tourists. India blamed Pakistan-based groups and launched airstrikes on militant sites. Pakistan retaliated with missiles and drones. A fragile ceasefire was brokered on May 10 with help from international powers, but border tensions and humanitarian issues persist.",
    "style": "neutral",
    "tone": "informative",
    "length": 500,
    "summary_length": 125
}

def main():
    """Main function to demonstrate the agentic article generation workflow."""
    try:
        # Initialize the agentic workflow
        print("Initializing Agentic Article Generation Workflow...")
        workflow = ArticleGenerationWorkflow()
        
        # Convert to JSON string
        input_json = json.dumps(crawler_data, indent=2)
        
        print("Input Data:")
        print(f"Title: {crawler_data['title']}")
        print(f"Keywords: {', '.join(crawler_data['keywords'])}")
        print(f"Target Length: {crawler_data['length']} words")
        print(f"Target Summary Length: {crawler_data['summary_length']} words")
        print(f"Style: {crawler_data['style']}")
        print(f"Tone: {crawler_data['tone']}")
        print("-" * 50)
        
        # Process the request using the agentic workflow
        print("Starting agentic article generation workflow...")
        output_json = workflow.execute_workflow(input_json)
        
        # Parse the output
        output_data = json.loads(output_json)
        
        if output_data["status"] == "success":
            print_success_results(output_data)
        else:
            print_error_results(output_data)
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1
    
    return 0

def print_success_results(output_data):
    """Print successful results in a formatted way."""
    print("\n" + "=" * 60)
    print("SUCCESS: Article Generated Successfully!")
    print("=" * 60)
    
    # Basic info
    print(f"\nGenerated Headline:")
    print(f"   {output_data['headline']}")
    
    metadata = output_data['metadata']
    
    # Quick stats
    print(f"\nQuick Stats:")
    print(f"   Article Words: {metadata['article']['word_count']} (target: {metadata['article']['target_length']})")
    print(f"   Summary Words: {metadata['summary']['word_count']} (target: {metadata['summary']['target_length']})")
    print(f"   Headline Words: {metadata['headline']['word_count']}")
    
    # Article content
    print(f"\nGenerated Article:")
    print("-" * 40)
    print(output_data["article_text"])
    
    # Summary content
    print(f"\nGenerated Summary:")
    print("-" * 40)
    print(output_data["summary"])
    
    # Detailed metadata
    print_detailed_metadata(metadata)

def print_detailed_metadata(metadata):
    """Print detailed metadata analysis."""
    print(f"\nDetailed Analysis:")
    print("-" * 40)
    
    # Article analysis
    article_meta = metadata['article']
    article_diff_pct = article_meta['length_difference_percentage']
    article_status = "Good" if article_diff_pct <= 20 else " Off target"
    print(f"Article Length: {article_status}")
    print(f"   Target: {article_meta['target_length']} words")
    print(f"   Actual: {article_meta['word_count']} words")
    print(f"   Difference: {article_diff_pct:.1f}%")
    
    # Summary analysis
    summary_meta = metadata['summary']
    summary_diff_pct = summary_meta['length_difference_percentage']
    summary_status = "Good" if summary_diff_pct <= 25 else "Off target"
    print(f"\nSummary Length: {summary_status}")
    print(f"   Target: {summary_meta['target_length']} words")
    print(f"   Actual: {summary_meta['word_count']} words")
    print(f"   Difference: {summary_diff_pct:.1f}%")
    
    # Headline analysis
    headline_meta = metadata['headline']
    headline_status = "Good" if headline_meta['word_count'] <= 12 else "Too long"
    print(f"\nHeadline Length: {headline_status}")
    print(f"   Words: {headline_meta['word_count']}")
    print(f"   Keywords present: {headline_meta['keywords_present']}")
    
    # Keyword coverage analysis
    print_keyword_analysis(metadata['keywords_coverage'])

def print_keyword_analysis(keywords_meta):
    """Print keyword coverage analysis."""
    print(f"\nKeyword Coverage Analysis:")
    
    total = keywords_meta['total']
    article_present = keywords_meta['article_coverage']['present']
    summary_present = keywords_meta['summary_coverage']['present']
    headline_present = keywords_meta['headline_coverage']['present']
    
    print(f"   Total keywords: {total}")
    print(f"   Article coverage: {article_present}/{total} ({(article_present/total)*100:.0f}%)")
    print(f"   Summary coverage: {summary_present}/{total} ({(summary_present/total)*100:.0f}%)")
    print(f"   Headline coverage: {headline_present}/{total} ({(headline_present/total)*100:.0f}%)")
    
    # Missing keywords
    article_missing = keywords_meta['article_coverage']['missing']
    summary_missing = keywords_meta['summary_coverage']['missing']
    
    if article_missing:
        print(f"   Missing from article: {', '.join(article_missing)}")
    if summary_missing:
        print(f"   Missing from summary: {', '.join(summary_missing)}")
    
    if not article_missing and not summary_missing:
        print("   All keywords successfully included!")

def print_error_results(output_data):
    """Print error results in a formatted way."""
    print("\n" + "=" * 60)
    print("ERROR: Article Generation Failed")
    print("=" * 60)
    
    print(f"Error Message: {output_data['message']}")
    print(f"Error Type: {output_data.get('error_type', 'Unknown')}")
    print(f"Agent: {output_data.get('agent', 'Unknown')}")
    print(f"Timestamp: {output_data.get('timestamp', 'Unknown')}")
    
    print("\n🔧 Troubleshooting Tips:")
    error_type = output_data.get('error_type', '')
    
    if 'json_parsing' in error_type:
        print("   - Check your input JSON format")
        print("   - Ensure all required fields are present")
    elif 'input_validation' in error_type:
        print("   - Verify required fields: title, keywords, summary")
        print("   - Check data types (length should be integer)")
    elif 'api' in error_type.lower() or 'groq' in output_data['message'].lower():
        print("   - Check your GROQ_API_KEY environment variable")
        print("   - Verify your internet connection")
        print("   - Check API rate limits")
    else:
        print("   - Check the logs above for more details")
        print("   - Ensure all dependencies are installed")

def save_results_to_file(output_data, filename="article_output.json"):
    """Save results to a JSON file for later use."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {filename}")
    except Exception as e:
        print(f"\nCould not save results to file: {str(e)}")

if __name__ == "__main__":
    # Run the main function
    exit_code = main()
    
    # Optional: Ask user if they want to save results
    try:
        save_choice = input("\nSave results to file? (y/n): ").strip().lower()
        if save_choice == 'y':
            # Re-run to get results for saving (in a real app, you'd store the results)
            workflow = ArticleGenerationWorkflow()
            input_json = json.dumps(crawler_data)
            output_json = workflow.execute_workflow(input_json)
            output_data = json.loads(output_json)
            save_results_to_file(output_data)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    
    exit(exit_code)