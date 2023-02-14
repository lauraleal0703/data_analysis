from .models.ticket import Ticket

def test():
    ticket = Ticket.get_by_tn("2023010354000189")
    return ticket