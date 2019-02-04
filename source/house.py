
import hashlib

class House(object):
    """
    Sold House class
    """
    def __init__(
            self,
            street_address=None,
            city=None,
            state=None,
            beds=None,
            baths=None,
            sq_ft=None,
            property_type=None,
            sold_price=None,
            years_built=None,
            days_on_market=None,
    ):
        self.street_address = street_address
        self.city = city
        self.state = state
        self.beds = beds
        self.baths = baths
        self.sq_ft = sq_ft
        self.property_type = property_type
        self.sold_price = sold_price
        self.year_built = years_built
        self.days_on_market = days_on_market

    @property
    def detailed(self):
        detail_string = "Address: %s\nProperty Type: %s\nBeds: %s\nBaths: %s\nSqFt: %s\n, Sold Price: %s\n"
        return detail_string % (
            str(self),
            self.property_type,
            self.beds,
            self.baths,
            self.sq_ft,
            self.sold_price
        )

    @property
    def street_address(self):
        return self._street_address

    @street_address.setter
    def street_address(self, street_address):
        self._street_address = street_address

    @property
    def beds(self):
        return self._beds

    @beds.setter
    def beds(self, beds):
        self._beds = beds

    @property
    def baths(self):
        return self._baths

    @baths.setter
    def baths(self, baths):
        self._baths = baths

    @property
    def sq_ft(self):
        return self._sq_ft

    @sq_ft.setter
    def sq_ft(self, sq_ft):
        self._sq_ft = sq_ft

    @property
    def property_type(self):
        return self._property_type

    @property_type.setter
    def property_type(self, property_type):
        self._property_type = property_type

    @property
    def sold_price(self):
        return self._sold_price

    @sold_price.setter
    def sold_price(self, sold_price):
        self._sold_price = sold_price

    @property
    def days_on_market(self):
        return self._days_on_market

    @days_on_market.setter
    def days_on_market(self, days_on_market):
        self._days_on_market = days_on_market

    @classmethod
    def from_dict(cls, dictionary):
        try:
            return cls(
                street_address=dictionary['street_address'],
                city=dictionary['city'],
                state=dictionary['state'],
                beds=dictionary['beds'],
                baths=dictionary['baths'],
                sq_ft=dictionary['sq_ft'],
                property_type=dictionary['property_type'],
                sold_price=dictionary['sold_price'],
                years_built=dictionary['year_built'],
                days_on_market=dictionary['days_on_market'], )
        except:
            return cls()

    def as_dict(self):
        d = {
            'street_address': self.street_address,
            'city': self.city,
            'state': self.state,
            'beds': self.beds,
            'baths': self.baths,
            'sq_ft': self.sq_ft,
            'property_type': self.property_type,
            'sold_price': self.sold_price,
            'year_built': self.year_built,
            'days_on_market': self.days_on_market
        }
        return d
