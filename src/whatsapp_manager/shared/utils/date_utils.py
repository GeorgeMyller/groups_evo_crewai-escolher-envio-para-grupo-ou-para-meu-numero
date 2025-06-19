"""
Utilitários de Data e Hora / Date and Time Utilities

PT-BR:
Funções utilitárias para manipulação de datas, horários e timestamps.

EN:
Utility functions for date, time, and timestamp manipulation.
"""

from datetime import datetime, timedelta
from typing import Union, Optional
import time


class DateUtils:
    """
    Utilitários para manipulação de data e hora
    Utilities for date and time manipulation
    """
    
    @staticmethod
    def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
        """
        Converte timestamp para datetime
        Converts timestamp to datetime
        
        Args:
            timestamp: Timestamp em segundos
            
        Returns:
            Objeto datetime
        """
        return datetime.fromtimestamp(timestamp)
    
    @staticmethod
    def datetime_to_timestamp(dt: datetime) -> int:
        """
        Converte datetime para timestamp
        Converts datetime to timestamp
        
        Args:
            dt: Objeto datetime
            
        Returns:
            Timestamp em segundos
        """
        return int(dt.timestamp())
    
    @staticmethod
    def string_to_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """
        Converte string para datetime
        Converts string to datetime
        
        Args:
            date_str: String de data
            format_str: Formato da string
            
        Returns:
            Objeto datetime
        """
        return datetime.strptime(date_str, format_str)
    
    @staticmethod
    def datetime_to_string(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Converte datetime para string
        Converts datetime to string
        
        Args:
            dt: Objeto datetime
            format_str: Formato desejado
            
        Returns:
            String formatada
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def get_date_range_last_days(days: int) -> tuple[datetime, datetime]:
        """
        Obtém intervalo dos últimos N dias
        Gets date range for last N days
        
        Args:
            days: Número de dias para trás
            
        Returns:
            Tupla (data_inicio, data_fim)
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def get_today_range() -> tuple[datetime, datetime]:
        """
        Obtém intervalo do dia atual (00:00 às 23:59)
        Gets today's range (00:00 to 23:59)
        
        Returns:
            Tupla (inicio_do_dia, fim_do_dia)
        """
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        return start_of_day, end_of_day
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Formata duração em segundos para string legível
        Formats duration in seconds to readable string
        
        Args:
            seconds: Duração em segundos
            
        Returns:
            String formatada (ex: "2h 30m", "45s")
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds > 0:
                return f"{minutes}m {remaining_seconds}s"
            else:
                return f"{minutes}m"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes > 0:
                return f"{hours}h {remaining_minutes}m"
            else:
                return f"{hours}h"
    
    @staticmethod
    def format_relative_time(dt: datetime) -> str:
        """
        Formata tempo relativo (ex: "há 2 horas", "ontem")
        Formats relative time (e.g., "2 hours ago", "yesterday")
        
        Args:
            dt: Datetime para comparar
            
        Returns:
            String de tempo relativo
        """
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            if diff.days == 1:
                return "ontem"
            elif diff.days < 7:
                return f"há {diff.days} dias"
            else:
                return dt.strftime("%d/%m/%Y")
        else:
            seconds = int(diff.total_seconds())
            if seconds < 60:
                return "agora"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"há {minutes} minuto{'s' if minutes > 1 else ''}"
            else:
                hours = seconds // 3600
                return f"há {hours} hora{'s' if hours > 1 else ''}"
    
    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """
        Verifica se duas datas são do mesmo dia
        Checks if two dates are on the same day
        
        Args:
            dt1: Primeira data
            dt2: Segunda data
            
        Returns:
            True se são do mesmo dia
        """
        return dt1.date() == dt2.date()
    
    @staticmethod
    def add_business_days(start_date: datetime, business_days: int) -> datetime:
        """
        Adiciona dias úteis a uma data
        Adds business days to a date
        
        Args:
            start_date: Data inicial
            business_days: Número de dias úteis a adicionar
            
        Returns:
            Nova data
        """
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            # Segunda (0) a Sexta (4) são dias úteis
            if current_date.weekday() < 5:
                days_added += 1
        
        return current_date
    
    @staticmethod
    def get_next_schedule_time(time_str: str) -> datetime:
        """
        Obtém próximo horário de agendamento
        Gets next schedule time
        
        Args:
            time_str: Horário no formato "HH:MM"
            
        Returns:
            Próximo datetime para o horário especificado
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            
            now = datetime.now()
            today_schedule = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Se o horário de hoje já passou, agendar para amanhã
            if today_schedule <= now:
                return today_schedule + timedelta(days=1)
            else:
                return today_schedule
                
        except ValueError:
            raise ValueError(f"Formato de horário inválido: {time_str}. Use HH:MM")
    
    @staticmethod
    def sleep_until(target_time: datetime):
        """
        Pausa execução até horário específico
        Sleeps until specific time
        
        Args:
            target_time: Horário alvo
        """
        now = datetime.now()
        if target_time > now:
            sleep_seconds = (target_time - now).total_seconds()
            time.sleep(sleep_seconds)
