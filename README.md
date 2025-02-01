# FleetControl
FleetControl: Restaurant Delivery Fleet Management FleetControl is a SaaS solution designed for restaurateurs to efficiently manage their delivery fleets and drivers. By integrating seamlessly with restaurant operations, this platform enables users to add and track delivery vehicles and drivers within their system.

## Installation

1. Clone the repository
2. Run `docker-compose up --build`
3. Run `docker-compose exec web python manage.py migrate`
4. Run `docker-compose exec web python manage.py createsuperuser`