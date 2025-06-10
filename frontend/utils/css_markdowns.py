CSS_MAIN = """
    <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
            margin-bottom: 1rem;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin: 0;
        }  
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin: 0;
        }
        .recent-case {
            background: #f8f9ff;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            border-left: 3px solid #4CAF50;
        }
        .status-completed {
            background-color: #e8f5e8;
            color: #2e7d32;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .status-progress {
            background-color: #fff3cd;
            color: #856404;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .sidebar-nav {
            padding: 0.5rem 0;
        }
        .nav-item {
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .nav-item:hover {
            background-color: #e3f2fd;
            transform: translateX(5px);
        }
        .nav-item.active {
            background-color: #667eea;
            color: white;
        } 
        .quick-action-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            margin: 0.25rem;
            cursor: pointer;
            transition: transform 0.2s ease;
        } 
        .quick-action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .chat-preview {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f0f2f6;
            border-radius: 10px 10px 0 0;
            padding-left: 12px;
            padding-right: 12px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #667eea;
            color: white;
        }
    </style>
"""
