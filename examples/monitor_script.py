#!/usr/bin/env python3
"""
Ejemplo de script de monitoreo automatizado.
Ejecuta escaneos periódicos y envía alertas para menciones importantes.
"""

import time
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import BrandMentionDetector


def monitor_brand(interval_minutes: int = 15):
    """
    Monitorea la marca en intervalos regulares.

    Args:
        interval_minutes: Intervalo entre escaneos en minutos
    """
    detector = BrandMentionDetector()

    print(f"🔍 Iniciando monitoreo de marca...")
    print(f"📊 Keywords: {', '.join(detector.brand_keywords)}")
    print(f"⏰ Intervalo: cada {interval_minutes} minutos")
    print(f"Press Ctrl+C to stop\n")

    try:
        while True:
            print(f"\n{'='*50}")
            print(f"🔄 Escaneando... ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            print(f"{'='*50}\n")

            # Scan Reddit
            detector.scan_reddit(limit=50, notify=True)

            # Show quick stats
            print("\n📈 Estadísticas actuales:")
            detector.show_stats()

            # Check for negative mentions (important for reputation)
            print("\n⚠️  Verificando menciones negativas recientes...")
            detector.show_by_sentiment('negative', limit=5)

            # Sleep until next scan
            print(f"\n💤 Próximo escaneo en {interval_minutes} minutos...")
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo monitoreo...")
        detector.close()
        print("✅ Cerrado correctamente")


def check_reputation():
    """Verificación rápida de reputación."""
    detector = BrandMentionDetector()

    try:
        print("📊 Análisis de Reputación\n")

        stats = detector.db.get_stats()

        if stats['total'] == 0:
            print("⚠️  No hay menciones en la base de datos.")
            print("💡 Ejecuta primero: python -m src.main scan")
            return

        # Calculate reputation score
        total = stats['total']
        pos_rate = (stats['positive'] / total) * 100 if total > 0 else 0
        neg_rate = (stats['negative'] / total) * 100 if total > 0 else 0

        reputation_score = pos_rate - neg_rate

        print(f"Total de menciones: {total}")
        print(f"Positivas: {stats['positive']} ({pos_rate:.1f}%)")
        print(f"Negativas: {stats['negative']} ({neg_rate:.1f}%)")
        print(f"Neutrales: {stats['neutral']}")
        print(f"\n🎯 Score de Reputación: {reputation_score:+.1f}")

        if reputation_score > 20:
            print("✅ Excelente reputación online")
        elif reputation_score > 0:
            print("👍 Reputación positiva")
        elif reputation_score > -20:
            print("⚠️  Reputación mixta - revisar menciones negativas")
        else:
            print("🚨 Alerta: Muchas menciones negativas - acción requerida")

        # Show recent negative mentions for action
        if stats['negative'] > 0:
            print("\n🔴 Menciones negativas recientes para atender:")
            detector.show_by_sentiment('negative', limit=5)

    finally:
        detector.close()


def find_link_opportunities():
    """Busca oportunidades de links y participación."""
    detector = BrandMentionDetector()

    try:
        print("🔗 Oportunidades de Links y Participación\n")

        # Get mentions with links
        mentions_with_links = detector.db.get_mentions_with_links(limit=20)

        if not mentions_with_links:
            print("ℹ️  No se encontraron menciones con links")
            return

        print(f"Encontradas {len(mentions_with_links)} menciones con links\n")

        for mention in mentions_with_links:
            sentiment_emoji = {
                'positive': '✅',
                'negative': '❌',
                'neutral': '⚪'
            }.get(mention.sentiment_label, '⚪')

            print(f"{sentiment_emoji} r/{mention.subreddit} - Score: {mention.post_score}")
            print(f"   👤 {mention.author}")
            print(f"   🔗 {mention.url}")
            print(f"   📝 {mention.content[:100]}...")
            print()

    finally:
        detector.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Brand Monitoring Scripts')
    parser.add_argument(
        'mode',
        choices=['monitor', 'reputation', 'links'],
        help='Modo de operación'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Intervalo en minutos para modo monitor (default: 15)'
    )

    args = parser.parse_args()

    if args.mode == 'monitor':
        monitor_brand(interval_minutes=args.interval)
    elif args.mode == 'reputation':
        check_reputation()
    elif args.mode == 'links':
        find_link_opportunities()
