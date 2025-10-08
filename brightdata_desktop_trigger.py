#!/usr/bin/env python3
"""
BrightData Desktop Trigger - Simple GUI app to trigger scrapers
"""
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import threading
import json

class BrightDataTrigger:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 BrightData Scraper Trigger")
        self.root.geometry("500x400")
        self.root.configure(bg='#f0f0f0')
        
        # API URL
        self.api_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/"
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="🚀 BrightData Scraper Trigger", 
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            self.root,
            text="Click any button to start scraping immediately!",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666'
        )
        desc_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
        # Instagram button
        self.instagram_btn = tk.Button(
            button_frame,
            text="📸 Trigger Instagram Scraper",
            font=('Arial', 12, 'bold'),
            bg='#E4405F',
            fg='white',
            width=25,
            height=2,
            command=lambda: self.trigger_scraper('instagram'),
            cursor='hand2'
        )
        self.instagram_btn.pack(pady=10)
        
        # Facebook button
        self.facebook_btn = tk.Button(
            button_frame,
            text="📘 Trigger Facebook Scraper",
            font=('Arial', 12, 'bold'),
            bg='#4267B2',
            fg='white',
            width=25,
            height=2,
            command=lambda: self.trigger_scraper('facebook'),
            cursor='hand2'
        )
        self.facebook_btn.pack(pady=10)
        
        # Both button
        self.both_btn = tk.Button(
            button_frame,
            text="🎯 Trigger Both Scrapers",
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            width=25,
            height=2,
            command=self.trigger_both,
            cursor='hand2'
        )
        self.both_btn.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready to trigger scrapers",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#333'
        )
        self.status_label.pack(pady=5)
        
        # Results text area
        self.results_text = tk.Text(
            self.root,
            height=8,
            width=60,
            font=('Consolas', 9),
            bg='#fafafa',
            fg='#333'
        )
        self.results_text.pack(pady=10, padx=20, fill='both', expand=True)
        
    def update_status(self, message, color='#333'):
        self.status_label.config(text=message, fg=color)
        self.root.update()
        
    def add_result(self, message):
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.root.update()
        
    def start_progress(self):
        self.progress.start(10)
        self.instagram_btn.config(state='disabled')
        self.facebook_btn.config(state='disabled')
        self.both_btn.config(state='disabled')
        
    def stop_progress(self):
        self.progress.stop()
        self.instagram_btn.config(state='normal')
        self.facebook_btn.config(state='normal')
        self.both_btn.config(state='normal')
        
    def trigger_scraper(self, platform):
        def run():
            try:
                self.start_progress()
                self.update_status(f"Starting {platform} scraper...", '#ff9800')
                self.add_result(f"🚀 Triggering {platform.title()} scraper...")
                
                urls = ['https://www.instagram.com/nike/', 'https://www.instagram.com/adidas/'] if platform == 'instagram' else ['https://www.facebook.com/nike', 'https://www.facebook.com/adidas']
                
                response = requests.post(
                    self.api_url,
                    json={
                        "platform": platform,
                        "urls": urls
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.update_status(f"✅ {platform.title()} scraper started!", '#4caf50')
                        self.add_result(f"✅ SUCCESS! {platform.title()} scraper started!")
                        self.add_result(f"📊 Job ID: {data.get('batch_job_id')}")
                        self.add_result(f"📊 Dataset: {data.get('dataset_id')}")
                        self.add_result(f"🔗 URLs: {data.get('urls_count')} URLs processed")
                        self.add_result("👉 Check your BrightData dashboard for progress!")
                        
                        messagebox.showinfo(
                            "Success!", 
                            f"{platform.title()} scraper started successfully!\n\nJob ID: {data.get('batch_job_id')}\n\nCheck BrightData dashboard for progress."
                        )
                    else:
                        error_msg = data.get('error', 'Unknown error')
                        self.update_status(f"❌ {platform.title()} failed", '#f44336')
                        self.add_result(f"❌ Error: {error_msg}")
                        messagebox.showerror("Error", f"Failed to start {platform} scraper:\n{error_msg}")
                else:
                    self.update_status(f"❌ HTTP {response.status_code}", '#f44336')
                    self.add_result(f"❌ HTTP Error: {response.status_code}")
                    messagebox.showerror("Error", f"HTTP Error {response.status_code}")
                    
            except Exception as e:
                self.update_status("❌ Connection failed", '#f44336')
                self.add_result(f"❌ Exception: {str(e)}")
                messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
            finally:
                self.stop_progress()
                
        # Run in separate thread to avoid blocking GUI
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        
    def trigger_both(self):
        def run():
            try:
                self.start_progress()
                self.update_status("Starting both scrapers...", '#ff9800')
                self.add_result("🎯 Triggering both Instagram and Facebook scrapers...")
                
                # Trigger Instagram
                self.add_result("📸 Starting Instagram...")
                instagram_response = requests.post(
                    self.api_url,
                    json={
                        "platform": "instagram",
                        "urls": ["https://www.instagram.com/nike/", "https://www.instagram.com/adidas/"]
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                instagram_success = False
                if instagram_response.status_code == 200:
                    instagram_data = instagram_response.json()
                    if instagram_data.get('success'):
                        instagram_success = True
                        self.add_result(f"✅ Instagram: {instagram_data.get('batch_job_id')}")
                    else:
                        self.add_result(f"❌ Instagram: {instagram_data.get('error')}")
                else:
                    self.add_result(f"❌ Instagram: HTTP {instagram_response.status_code}")
                
                # Trigger Facebook
                self.add_result("📘 Starting Facebook...")
                facebook_response = requests.post(
                    self.api_url,
                    json={
                        "platform": "facebook",
                        "urls": ["https://www.facebook.com/nike", "https://www.facebook.com/adidas"]
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                facebook_success = False
                if facebook_response.status_code == 200:
                    facebook_data = facebook_response.json()
                    if facebook_data.get('success'):
                        facebook_success = True
                        self.add_result(f"✅ Facebook: {facebook_data.get('batch_job_id')}")
                    else:
                        self.add_result(f"❌ Facebook: {facebook_data.get('error')}")
                else:
                    self.add_result(f"❌ Facebook: HTTP {facebook_response.status_code}")
                
                # Final status
                if instagram_success and facebook_success:
                    self.update_status("✅ Both scrapers started!", '#4caf50')
                    messagebox.showinfo("Success!", "Both scrapers started successfully!\n\nCheck BrightData dashboard for progress.")
                elif instagram_success or facebook_success:
                    self.update_status("⚠️ Partial success", '#ff9800')
                    messagebox.showwarning("Partial Success", "One scraper started successfully.\n\nCheck results above for details.")
                else:
                    self.update_status("❌ Both failed", '#f44336')
                    messagebox.showerror("Error", "Both scrapers failed to start.\n\nCheck results above for details.")
                    
            except Exception as e:
                self.update_status("❌ Connection failed", '#f44336')
                self.add_result(f"❌ Exception: {str(e)}")
                messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
            finally:
                self.stop_progress()
                
        # Run in separate thread
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BrightDataTrigger(root)
    root.mainloop()