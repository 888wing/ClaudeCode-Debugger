# ai-integration-agent

**Purpose**: 實現智能分析和建議功能

**Activation**: 
- Manual: `--agent ai-integration-agent`
- Automatic: AI analysis, similarity matching, recommendation systems, learning features

**Core Capabilities**:
- 錯誤相似度計算
- 歷史記錄分析
- 解決方案推薦
- 上下文增強
- 學習系統設計
- Pattern recognition
- Success rate tracking

**Specialized Knowledge**:
- Text similarity algorithms (cosine, Jaccard)
- Machine learning for classification
- History database design
- Recommendation algorithms
- Context extraction techniques
- Performance metrics

**Integration Points**:
- Works with error-pattern-agent for feature extraction
- Coordinates with template-system-agent for enhanced prompts
- Integrates with Analyzer persona for root cause analysis
- Leverages Performance persona for optimization

**Error Analysis System**:

### ErrorAnalyzer Class
```python
class ErrorAnalyzer:
    def __init__(self):
        self.history_db = HistoryDatabase()
        self.similarity_engine = SimilarityEngine()
        self.recommendation_system = RecommendationSystem()
        
    def analyze(self, error_text: str, error_type: str) -> Dict:
        """Comprehensive error analysis"""
        return {
            'severity': self._assess_severity(error_text, error_type),
            'similar_errors': self._find_similar_errors(error_text),
            'suggested_solutions': self._get_suggestions(error_text, error_type),
            'estimated_time': self._estimate_fix_time(error_text),
            'confidence_score': self._calculate_confidence(),
            'context_hints': self._extract_context_hints(error_text),
        }
    
    def _assess_severity(self, error_text: str, error_type: str) -> str:
        """Assess error severity using multiple factors"""
        factors = {
            'build_blocking': 'build' in error_text.lower(),
            'production_impact': self._check_production_keywords(error_text),
            'security_related': self._check_security_keywords(error_text),
            'data_loss_risk': self._check_data_loss_keywords(error_text),
            'user_facing': self._check_user_impact(error_text),
        }
        
        # Weighted scoring
        score = sum([
            factors['build_blocking'] * 0.3,
            factors['production_impact'] * 0.25,
            factors['security_related'] * 0.2,
            factors['data_loss_risk'] * 0.15,
            factors['user_facing'] * 0.1,
        ])
        
        if score >= 0.7: return 'critical'
        elif score >= 0.5: return 'high'
        elif score >= 0.3: return 'medium'
        else: return 'low'
```

### History Management
```python
class HistoryDatabase:
    def __init__(self, db_path: Path = Path.home() / '.ccdebug'):
        self.db_path = db_path / 'history.db'
        self.init_database()
        
    def save_error_resolution(self, error_hash: str, resolution: Dict):
        """Save successful error resolution"""
        entry = {
            'error_hash': error_hash,
            'error_text': resolution['error_text'],
            'error_type': resolution['error_type'],
            'solution': resolution['solution'],
            'fix_time': resolution['fix_time'],
            'success_rate': resolution['success_rate'],
            'timestamp': datetime.now().isoformat(),
            'tags': resolution.get('tags', []),
        }
        # Store in SQLite or JSON
        
    def search_similar(self, error_text: str, threshold: float = 0.7) -> List[Dict]:
        """Find similar historical errors"""
        # Implement similarity search
        pass
```

### Similarity Engine
```python
class SimilarityEngine:
    def __init__(self):
        self.vectorizer = self._init_vectorizer()
        
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two error texts"""
        # Preprocess texts
        text1_clean = self._preprocess(text1)
        text2_clean = self._preprocess(text2)
        
        # Multiple similarity metrics
        cosine_sim = self._cosine_similarity(text1_clean, text2_clean)
        jaccard_sim = self._jaccard_similarity(text1_clean, text2_clean)
        structure_sim = self._structural_similarity(text1, text2)
        
        # Weighted combination
        return (cosine_sim * 0.5 + jaccard_sim * 0.3 + structure_sim * 0.2)
```

### Context Enhancement
```python
class ContextCollector:
    def collect_context(self, error_text: str) -> Dict:
        """Collect relevant context for better debugging"""
        return {
            'git_info': self._get_git_context(),
            'environment': self._get_environment_info(),
            'dependencies': self._get_dependency_info(),
            'recent_changes': self._get_recent_changes(),
            'related_files': self._find_related_files(error_text),
        }
    
    def _get_git_context(self) -> Dict:
        """Get Git repository context"""
        return {
            'current_branch': self._get_current_branch(),
            'last_commit': self._get_last_commit(),
            'unstaged_changes': self._get_unstaged_files(),
            'merge_conflicts': self._check_merge_conflicts(),
        }
```

### Recommendation System
```python
class RecommendationSystem:
    def get_recommendations(self, error_analysis: Dict) -> List[Dict]:
        """Get solution recommendations based on analysis"""
        recommendations = []
        
        # Historical solutions
        if error_analysis['similar_errors']:
            for similar in error_analysis['similar_errors']:
                if similar['success_rate'] > 0.8:
                    recommendations.append({
                        'type': 'historical',
                        'solution': similar['solution'],
                        'confidence': similar['success_rate'],
                        'estimated_time': similar['fix_time'],
                    })
        
        # Pattern-based recommendations
        pattern_recs = self._get_pattern_recommendations(
            error_analysis['error_type'],
            error_analysis['error_features']
        )
        recommendations.extend(pattern_recs)
        
        # Sort by confidence
        return sorted(recommendations, 
                     key=lambda x: x['confidence'], 
                     reverse=True)[:5]
```

**Learning Features**:
- Success rate tracking
- Solution effectiveness measurement
- Pattern evolution
- User feedback integration
- Continuous improvement