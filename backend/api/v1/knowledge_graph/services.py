import networkx as nx
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from . import models


class KnowledgeGraphService:
    """Service for building and analyzing knowledge graphs"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.concepts = {}
        self.prerequisites = {}
    
    async def build_subject_graph(self, db: Session, subject: str) -> nx.DiGraph:
        """Build knowledge graph for a specific subject"""
        # Get all concepts for the subject
        concepts = db.query(models.Concept).filter(
            models.Concept.subject == subject
        ).all()
        
        # Get all relationships for the subject
        relationships = db.query(models.ConceptRelationship).join(
            models.Concept, models.ConceptRelationship.source_concept_id == models.Concept.id
        ).filter(models.Concept.subject == subject).all()
        
        # Build NetworkX graph
        self.graph.clear()
        
        # Add nodes (concepts)
        for concept in concepts:
            self.graph.add_node(concept.id, 
                              name=concept.name,
                              description=concept.description,
                              difficulty_level=concept.difficulty_level,
                              subject=concept.subject)
        
        # Add edges (relationships)
        for relationship in relationships:
            self.graph.add_edge(relationship.source_concept_id,
                              relationship.target_concept_id,
                              relationship_type=relationship.relationship_type,
                              strength=relationship.strength)
        
        return self.graph
    
    async def find_learning_path(self, db: Session, user_id: int, subject: str, 
                                target_concepts: Set[int]) -> List[Dict[str, Any]]:
        """Find optimal learning path for user"""
        # Get user's current knowledge
        user_mastery = db.query(models.ConceptMastery).filter(
            models.ConceptMastery.user_id == user_id
        ).all()
        
        mastered_concepts = {cm.concept_id for cm in user_mastery if cm.mastery_level >= 0.8}
        
        # Build subject graph
        await self.build_subject_graph(db, subject)
        
        # Find shortest path to target concepts
        learning_path = []
        
        for target_concept in target_concepts:
            if target_concept in mastered_concepts:
                continue
            
            # Find shortest path from mastered concepts to target
            shortest_path = None
            min_distance = float('inf')
            
            for mastered_concept in mastered_concepts:
                try:
                    path = nx.shortest_path(self.graph, mastered_concept, target_concept)
                    if len(path) < min_distance:
                        shortest_path = path
                        min_distance = len(path)
                except nx.NetworkXNoPath:
                    continue
            
            if shortest_path:
                learning_path.extend(shortest_path[1:])  # Exclude starting point
        
        # Remove duplicates while preserving order
        seen = set()
        unique_path = []
        for concept_id in learning_path:
            if concept_id not in seen:
                unique_path.append(concept_id)
                seen.add(concept_id)
        
        # Get concept details
        path_concepts = []
        for concept_id in unique_path:
            concept = db.query(models.Concept).filter(models.Concept.id == concept_id).first()
            if concept:
                path_concepts.append({
                    "id": concept.id,
                    "name": concept.name,
                    "description": concept.description,
                    "difficulty_level": concept.difficulty_level
                })
        
        return path_concepts
    
    async def identify_knowledge_gaps(self, db: Session, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Identify knowledge gaps for user"""
        # Get user's mastery levels
        user_mastery = db.query(models.ConceptMastery).filter(
            models.ConceptMastery.user_id == user_id
        ).all()
        
        mastery_dict = {cm.concept_id: cm.mastery_level for cm in user_mastery}
        
        # Get all concepts for subject
        concepts = db.query(models.Concept).filter(
            models.Concept.subject == subject
        ).all()
        
        # Build graph
        await self.build_subject_graph(db, subject)
        
        knowledge_gaps = []
        
        for concept in concepts:
            concept_id = concept.id
            current_mastery = mastery_dict.get(concept_id, 0.0)
            
            if current_mastery < 0.8:  # Consider mastery threshold
                # Check prerequisites
                prerequisites = list(self.graph.predecessors(concept_id))
                missing_prerequisites = []
                
                for prereq_id in prerequisites:
                    prereq_mastery = mastery_dict.get(prereq_id, 0.0)
                    if prereq_mastery < 0.8:
                        missing_prerequisites.append(prereq_id)
                
                if missing_prerequisites:
                    # Missing prerequisites
                    gap_type = "missing_prerequisite"
                    severity = len(missing_prerequisites) / len(prerequisites) if prerequisites else 1.0
                else:
                    # Weak understanding
                    gap_type = "weak_understanding"
                    severity = 1.0 - current_mastery
                
                if severity > 0.3:  # Only report significant gaps
                    knowledge_gaps.append({
                        "concept_id": concept_id,
                        "concept_name": concept.name,
                        "gap_type": gap_type,
                        "severity": severity,
                        "current_mastery": current_mastery,
                        "missing_prerequisites": missing_prerequisites
                    })
        
        return knowledge_gaps
    
    async def recommend_next_concepts(self, db: Session, user_id: int, subject: str, 
                                    limit: int = 5) -> List[Dict[str, Any]]:
        """Recommend next concepts for user to learn"""
        # Get user's current knowledge
        user_mastery = db.query(models.ConceptMastery).filter(
            models.ConceptMastery.user_id == user_id
        ).all()
        
        mastered_concepts = {cm.concept_id for cm in user_mastery if cm.mastery_level >= 0.8}
        in_progress_concepts = {cm.concept_id for cm in user_mastery if 0.3 <= cm.mastery_level < 0.8}
        
        # Build graph
        await self.build_subject_graph(db, subject)
        
        # Find concepts that are ready to learn
        ready_concepts = []
        
        for node in self.graph.nodes():
            if node in mastered_concepts or node in in_progress_concepts:
                continue
            
            # Check if all prerequisites are mastered
            prerequisites = list(self.graph.predecessors(node))
            if all(prereq in mastered_concepts for prereq in prerequisites):
                ready_concepts.append(node)
        
        # Sort by difficulty level and recommend
        recommendations = []
        for concept_id in ready_concepts[:limit]:
            concept = db.query(models.Concept).filter(models.Concept.id == concept_id).first()
            if concept:
                recommendations.append({
                    "id": concept.id,
                    "name": concept.name,
                    "description": concept.description,
                    "difficulty_level": concept.difficulty_level,
                    "readiness_score": 1.0  # All prerequisites met
                })
        
        return recommendations
    
    async def analyze_learning_style(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Analyze user's learning style based on performance patterns"""
        # Get user's concept mastery data
        mastery_data = db.query(models.ConceptMastery).filter(
            models.ConceptMastery.user_id == user_id
        ).all()
        
        # Analyze patterns (simplified)
        visual_score = 0
        auditory_score = 0
        kinesthetic_score = 0
        
        for mastery in mastery_data:
            # This is a simplified analysis
            # In a real implementation, you'd analyze actual learning patterns
            if mastery.learning_style:
                if mastery.learning_style == "visual":
                    visual_score += mastery.mastery_level
                elif mastery.learning_style == "auditory":
                    auditory_score += mastery.mastery_level
                elif mastery.learning_style == "kinesthetic":
                    kinesthetic_score += mastery.mastery_level
        
        # Determine dominant learning style
        scores = {
            "visual": visual_score,
            "auditory": auditory_score,
            "kinesthetic": kinesthetic_score
        }
        
        dominant_style = max(scores, key=scores.get)
        
        return {
            "dominant_style": dominant_style,
            "style_scores": scores,
            "recommendations": {
                "visual": "Use diagrams, charts, and visual aids",
                "auditory": "Focus on audio content and discussions",
                "kinesthetic": "Include hands-on activities and experiments"
            }
        }


# Global instance
knowledge_graph_service = KnowledgeGraphService() 