"""
Rule-based FAQ chatbot module
"""

import json
import os
import re
import time
from typing import Dict, List, Tuple, Optional
import logging
from .utils.logger import ChatbotLogger


class FAQChatbot:
    """Rule-based FAQ chatbot for student queries."""
    
    def __init__(self, config):
        """
        Initialize FAQ chatbot.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = ChatbotLogger("chatbot")
        self.faq_data = {}
        self.synonyms = {}
        self.load_faq_data()
        self.load_synonyms()
    
    def load_faq_data(self) -> Dict[str, str]:
        """
        Load FAQ data from JSON file.
        
        Returns:
            Dictionary of FAQ questions and answers
        """
        if not os.path.exists(self.config.faq_file):
            self._create_default_faq()
        
        try:
            with open(self.config.faq_file, 'r', encoding='utf-8') as f:
                self.faq_data = json.load(f)
            
            self.logger.log_faq_loaded(len(self.faq_data))
            return self.faq_data
            
        except (json.JSONDecodeError, IOError) as e:
            self.logger.logger.error(f"Failed to load FAQ data: {e}")
            self._create_default_faq()
            return self.faq_data
    
    def _create_default_faq(self):
        """Create default FAQ data if file doesn't exist."""
        self.faq_data = {
            "attendance": {
                "keywords": ["attendance", "present", "absent", "mark", "check"],
                "answer": "Attendance is automatically marked using face recognition when you enter the classroom. You can check your attendance records on the student portal.",
                "category": "attendance"
            },
            "exam schedule": {
                "keywords": ["exam", "schedule", "date", "time", "when"],
                "answer": "Exam schedules are available on the academic calendar and student portal. Please check the official website for the most up-to-date information.",
                "category": "academic"
            },
            "leave policy": {
                "keywords": ["leave", "absence", "sick", "emergency", "permission"],
                "answer": "Leave requests must be submitted through the student portal at least 24 hours in advance. Emergency leaves require immediate notification to the academic office.",
                "category": "policies"
            },
            "makeup exam": {
                "keywords": ["makeup", "retake", "resit", "missed exam"],
                "answer": "Makeup exams require prior approval from the academic office. You must submit a valid reason with supporting documents within 48 hours of the original exam.",
                "category": "academic"
            },
            "attendance report": {
                "keywords": ["report", "record", "history", "percentage"],
                "answer": "Your attendance reports are available on the student portal. You can view daily, weekly, and monthly attendance summaries.",
                "category": "attendance"
            },
            "grades": {
                "keywords": ["grade", "marks", "score", "result", "gpa"],
                "answer": "Grades and results are published on the student portal within 2 weeks after each exam. You can also request a grade review if needed.",
                "category": "academic"
            },
            "library": {
                "keywords": ["library", "book", "borrow", "return", "fine"],
                "answer": "The library is open Monday to Friday 8 AM to 8 PM, Saturday 9 AM to 5 PM. You can borrow up to 5 books for 2 weeks. Late returns incur fines.",
                "category": "facilities"
            },
            "cafeteria": {
                "keywords": ["cafeteria", "food", "lunch", "meal", "dining"],
                "answer": "The cafeteria serves breakfast (7-9 AM), lunch (12-2 PM), and dinner (6-8 PM). You can pay with student ID card or cash.",
                "category": "facilities"
            },
            "parking": {
                "keywords": ["parking", "vehicle", "car", "bike", "space"],
                "answer": "Student parking is available in designated areas. A parking permit is required and can be obtained from the security office.",
                "category": "facilities"
            },
            "contact": {
                "keywords": ["contact", "help", "support", "phone", "email"],
                "answer": "For general inquiries, contact the student services office at (555) 123-4567 or email studentservices@university.edu. For technical issues, contact IT support.",
                "category": "support"
            }
        }
        
        self._save_faq_data()
        self.logger.logger.info("Created default FAQ data")
    
    def load_synonyms(self):
        """Load synonyms for better keyword matching."""
        self.synonyms = {
            "attendance": ["attendance", "present", "absent", "mark", "check", "roll call"],
            "exam": ["exam", "test", "quiz", "assessment", "evaluation"],
            "leave": ["leave", "absence", "sick", "emergency", "permission", "holiday"],
            "grade": ["grade", "marks", "score", "result", "gpa", "points"],
            "library": ["library", "book", "borrow", "return", "fine", "catalog"],
            "food": ["food", "cafeteria", "lunch", "meal", "dining", "eat"],
            "parking": ["parking", "vehicle", "car", "bike", "space", "garage"],
            "help": ["help", "support", "contact", "phone", "email", "assistance"]
        }
    
    def _save_faq_data(self):
        """Save FAQ data to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config.faq_file), exist_ok=True)
            
            with open(self.config.faq_file, 'w', encoding='utf-8') as f:
                json.dump(self.faq_data, f, indent=4, ensure_ascii=False)
                
        except IOError as e:
            self.logger.logger.error(f"Failed to save FAQ data: {e}")
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess user query for better matching.
        
        Args:
            query: Raw user query
            
        Returns:
            Preprocessed query string
        """
        # Convert to lowercase
        query = query.lower()
        
        # Remove special characters and extra spaces
        query = re.sub(r'[^\w\s]', ' ', query)
        query = ' '.join(query.split())
        
        return query
    
    def find_best_match(self, query: str) -> Tuple[Optional[str], float]:
        """
        Find the best matching FAQ entry for a query.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (best_match_key, confidence_score)
        """
        query = self.preprocess_query(query)
        query_words = set(query.split())
        
        best_match = None
        best_score = 0.0
        
        for key, data in self.faq_data.items():
            keywords = set(data.get("keywords", []))
            
            # Calculate match score
            common_words = query_words.intersection(keywords)
            score = len(common_words) / max(len(keywords), 1)
            
            # Check synonyms
            for word in query_words:
                for synonym_group in self.synonyms.values():
                    if word in synonym_group:
                        for synonym in synonym_group:
                            if synonym in keywords:
                                score += 0.5 / max(len(keywords), 1)
                                break
            
            if score > best_score:
                best_score = score
                best_match = key
        
        return best_match, best_score
    
    def get_response(self, query: str) -> str:
        """
        Get response for user query.
        
        Args:
            query: User query
            
        Returns:
            Bot response
        """
        start_time = time.time()
        
        if not query.strip():
            response = "Please ask a question. I can help with attendance, exams, policies, and more!"
            self.logger.log_query(query, response)
            return response
        
        best_match, confidence = self.find_best_match(query)
        
        if best_match and confidence > 0.3:  # Minimum confidence threshold
            response = self.faq_data[best_match]["answer"]
            category = self.faq_data[best_match].get("category", "general")
            
            # Add helpful context
            if category == "attendance":
                response += "\n\n💡 Tip: Make sure to face the camera clearly for accurate attendance marking."
            elif category == "academic":
                response += "\n\n📚 Check the student portal for the latest academic information."
            elif category == "policies":
                response += "\n\n📋 For detailed policies, visit the student handbook."
            
        else:
            response = self._get_fallback_response(query)
            self.logger.log_unknown_query(query)
        
        response_time = time.time() - start_time
        self.logger.log_query(query, response, response_time)
        
        return response
    
    def _get_fallback_response(self, query: str) -> str:
        """
        Generate fallback response for unmatched queries.
        
        Args:
            query: User query
            
        Returns:
            Fallback response
        """
        fallback_responses = [
            "I'm not sure about that specific question. Could you try rephrasing it?",
            "That's a good question! I don't have information about that topic yet.",
            "I didn't understand that. Try asking about attendance, exams, or policies.",
            "Sorry, I don't have an answer for that. Please contact student services for specific inquiries.",
            "I'm still learning! Could you ask about attendance, grades, or campus facilities?"
        ]
        
        # Simple keyword-based suggestions
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["attendance", "present", "absent"]):
            return "I can help with attendance questions! Ask about marking attendance, checking records, or attendance policies."
        elif any(word in query_lower for word in ["exam", "test", "grade"]):
            return "I can help with academic questions! Ask about exam schedules, grades, or academic policies."
        elif any(word in query_lower for word in ["help", "support", "contact"]):
            return "For immediate help, contact student services at (555) 123-4567 or visit the student portal."
        else:
            import random
            return random.choice(fallback_responses)
    
    def add_faq_entry(self, question: str, answer: str, keywords: List[str], category: str = "general"):
        """
        Add a new FAQ entry.
        
        Args:
            question: FAQ question
            answer: FAQ answer
            keywords: List of keywords for matching
            category: FAQ category
        """
        key = question.lower().replace(" ", "_").replace("?", "")
        
        self.faq_data[key] = {
            "keywords": keywords,
            "answer": answer,
            "category": category
        }
        
        self._save_faq_data()
        self.logger.logger.info(f"Added new FAQ entry: {key}")
    
    def get_categories(self) -> List[str]:
        """Get list of FAQ categories."""
        categories = set()
        for data in self.faq_data.values():
            categories.add(data.get("category", "general"))
        return sorted(list(categories))
    
    def get_faqs_by_category(self, category: str) -> Dict[str, Dict]:
        """Get FAQ entries for a specific category."""
        return {key: data for key, data in self.faq_data.items() 
                if data.get("category") == category}
    
    def start_chat(self):
        """Start interactive chatbot session."""
        print("\n" + "=" * 60)
        print("🤖 FAQ Chatbot - Smart Assistant")
        print("=" * 60)
        print("💬 I can help you with:")
        print("   • 📸 Attendance queries")
        print("   • 📚 Academic questions")
        print("   • 📋 Policies and procedures")
        print("   • 🏫 Campus facilities")
        print("   • 🆘 General support")
        print("\n💡 Tips:")
        print("   • Ask specific questions for better answers")
        print("   • Use keywords like 'attendance', 'exam', 'leave'")
        print("   • Type 'help' for more options")
        print("   • Type 'exit' to quit")
        print("=" * 60)
        
        conversation_count = 0
        
        while True:
            try:
                query = input(f"\n🤖 You: ").strip()
                
                if not query:
                    continue
                
                # Handle special commands
                if query.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Thank you for using the FAQ Chatbot!")
                    print("💡 Remember: I'm here whenever you need help!")
                    break
                
                elif query.lower() in ['help', 'commands']:
                    self._show_help()
                    continue
                
                elif query.lower() in ['categories', 'topics']:
                    self._show_categories()
                    continue
                
                elif query.lower() in ['stats', 'statistics']:
                    self._show_statistics()
                    continue
                
                # Get and display response
                response = self.get_response(query)
                conversation_count += 1
                
                print(f"\n🤖 Bot: {response}")
                
                # Show conversation progress
                if conversation_count % 5 == 0:
                    print(f"\n💬 Conversation count: {conversation_count}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chatbot session ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                self.logger.logger.error(f"Chatbot error: {e}")
    
    def _show_help(self):
        """Show help information."""
        print("\n📖 HELP - Available Commands:")
        print("• Type any question to get an answer")
        print("• 'help' - Show this help message")
        print("• 'categories' - Show available topics")
        print("• 'stats' - Show chatbot statistics")
        print("• 'exit' - Quit the chatbot")
        print("\n💡 Example Questions:")
        print("• 'How does attendance work?'")
        print("• 'When are the exams?'")
        print("• 'What is the leave policy?'")
        print("• 'Where is the library?'")
    
    def _show_categories(self):
        """Show available FAQ categories."""
        categories = self.get_categories()
        print(f"\n📂 Available Categories ({len(categories)}):")
        
        for category in categories:
            count = len(self.get_faqs_by_category(category))
            icon = self._get_category_icon(category)
            print(f"   {icon} {category.title()} ({count} entries)")
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for category."""
        icons = {
            "attendance": "📸",
            "academic": "📚",
            "policies": "📋",
            "facilities": "🏫",
            "support": "🆘",
            "general": "💬"
        }
        return icons.get(category, "💬")
    
    def _show_statistics(self):
        """Show chatbot statistics."""
        total_faqs = len(self.faq_data)
        categories = len(self.get_categories())
        
        print(f"\n📊 Chatbot Statistics:")
        print(f"   📝 Total FAQ entries: {total_faqs}")
        print(f"   📂 Categories: {categories}")
        print(f"   🎯 Keywords: {sum(len(data.get('keywords', [])) for data in self.faq_data.values())}")
        
        # Show category breakdown
        print(f"\n📈 Category Breakdown:")
        for category in self.get_categories():
            count = len(self.get_faqs_by_category(category))
            percentage = (count / total_faqs) * 100
            icon = self._get_category_icon(category)
            print(f"   {icon} {category.title()}: {count} ({percentage:.1f}%)")
