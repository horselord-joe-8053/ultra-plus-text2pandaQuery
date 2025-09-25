from typing import Dict, Any, List, Optional, Tuple, cast
from pathlib import Path
import pandas as pd
from flask import jsonify, request, send_from_directory

from config.logging_config import get_api_logger
from query_syn.engine import QuerySynthesisEngine


logger = get_api_logger()


def register_routes(app, rag_system: QuerySynthesisEngine):
    @app.get('/health')
    def health_check():
        stats = rag_system.get_stats()
        return jsonify({
            'status': 'healthy',
            'message': 'Query Synthesis API is running',
            'total_records': stats.get('total_records', 0),
            'dealers_count': stats.get('dealers_count', 0)
        })

    @app.post('/ask-api')
    def ask_question():
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Missing question field'}), 400
        question = str(data['question']).strip()
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        logger.info("/ask-api received question: %s", question)
        
        result = rag_system.answer_question(question)

        answer_out: str = str(result.get('answer', ''))
        sources_out: List[Dict[str, Any]] = result.get('sources') or []
        confidence_out: str = result.get('confidence') or 'unknown'
        query_spec = result.get('query_spec')
        logger.info("/ask-api produced answer length=%s, sources=%s",
                    len(answer_out), len(sources_out))

        return jsonify({
            'question': question,
            'sensitized_question': question,
            'answer': answer_out,
            'sources': sources_out,
            'confidence': str(confidence_out),
            'timestamp': pd.Timestamp.now().isoformat(),
            'query_spec': query_spec,
        })
    

    # Backward-compatibility with previous '/ask' endpoint
    @app.post('/ask')
    def ask_question_compat():
        return ask_question()

    # Search endpoint removed (no vector search in query synthesis mode)

    @app.get('/stats')
    def get_stats():
        return jsonify(rag_system.get_stats())

    # Sensitization stats endpoint optional; remove if fully de-identification is not used

    # Rebuild index endpoint removed (no embeddings/index in query synthesis mode)

    # Reports serving removed (no report generation in query synthesis mode)


