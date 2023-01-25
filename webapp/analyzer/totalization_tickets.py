from .otrs.models.ticket import Ticket

def algo() -> list:
    start_date = "2018-01-01"
    end_date = "2023-01-24"
    tickets_queue = Ticket.tickets_by_queue_date(6, start_date , end_date)
    return tickets_queue