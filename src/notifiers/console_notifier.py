"""Console notification system using Rich."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import List
from ..storage.database import Mention


class ConsoleNotifier:
    """Notifier that displays mentions in the console."""

    def __init__(self):
        """Initialize console notifier."""
        self.console = Console()

    def notify_new_mention(self, mention: Mention):
        """Display notification for a new mention."""
        # Choose color based on sentiment
        if mention.sentiment_label == 'positive':
            color = 'green'
            emoji = '✓'
        elif mention.sentiment_label == 'negative':
            color = 'red'
            emoji = '✗'
        else:
            color = 'yellow'
            emoji = '○'

        # Create panel
        title = f"{emoji} New Mention on {mention.platform.upper()}"

        content = f"""
[bold]Author:[/bold] {mention.author}
[bold]Subreddit:[/bold] r/{mention.subreddit if mention.subreddit else 'N/A'}
[bold]Sentiment:[/bold] [{color}]{mention.sentiment_label}[/{color}] ({mention.sentiment_score:.2f})
[bold]Score:[/bold] {mention.post_score}
[bold]Has Links:[/bold] {'Yes' if mention.has_links else 'No'}
[bold]URL:[/bold] {mention.url}

[bold]Content:[/bold]
{mention.content[:200]}{'...' if len(mention.content) > 200 else ''}
"""

        panel = Panel(
            content.strip(),
            title=title,
            border_style=color,
            expand=False
        )

        self.console.print(panel)

    def display_mentions_table(self, mentions: List[Mention], title: str = "Brand Mentions"):
        """Display mentions in a table format."""
        table = Table(title=title)

        table.add_column("Platform", style="cyan")
        table.add_column("Author", style="magenta")
        table.add_column("Sentiment", style="yellow")
        table.add_column("Score")
        table.add_column("Links")
        table.add_column("Subreddit")
        table.add_column("Date")

        for mention in mentions:
            # Sentiment color
            if mention.sentiment_label == 'positive':
                sentiment = f"[green]{mention.sentiment_label}[/green]"
            elif mention.sentiment_label == 'negative':
                sentiment = f"[red]{mention.sentiment_label}[/red]"
            else:
                sentiment = f"[yellow]{mention.sentiment_label}[/yellow]"

            links = "✓" if mention.has_links else "✗"

            table.add_row(
                mention.platform,
                mention.author[:20] if mention.author else 'N/A',
                sentiment,
                str(mention.post_score),
                links,
                mention.subreddit[:20] if mention.subreddit else 'N/A',
                mention.detected_at.strftime('%Y-%m-%d %H:%M')
            )

        self.console.print(table)

    def display_stats(self, stats: dict):
        """Display statistics about mentions."""
        table = Table(title="📊 Brand Mention Statistics", show_header=False)

        table.add_column("Metric", style="cyan bold")
        table.add_column("Value", style="magenta")

        table.add_row("Total Mentions", str(stats['total']))
        table.add_row("Positive", f"[green]{stats['positive']}[/green]")
        table.add_row("Negative", f"[red]{stats['negative']}[/red]")
        table.add_row("Neutral", f"[yellow]{stats['neutral']}[/yellow]")
        table.add_row("With Links", str(stats['with_links']))

        # Calculate percentages
        if stats['total'] > 0:
            pos_pct = (stats['positive'] / stats['total']) * 100
            neg_pct = (stats['negative'] / stats['total']) * 100
            link_pct = (stats['with_links'] / stats['total']) * 100

            table.add_row("", "")
            table.add_row("Positive Rate", f"{pos_pct:.1f}%")
            table.add_row("Negative Rate", f"{neg_pct:.1f}%")
            table.add_row("Link Rate", f"{link_pct:.1f}%")

        self.console.print(table)

    def display_success(self, message: str):
        """Display success message."""
        self.console.print(f"[green]✓[/green] {message}")

    def display_error(self, message: str):
        """Display error message."""
        self.console.print(f"[red]✗[/red] {message}")

    def display_info(self, message: str):
        """Display info message."""
        self.console.print(f"[blue]ℹ[/blue] {message}")

    def display_warning(self, message: str):
        """Display warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
