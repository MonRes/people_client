import requests
import hashlib
import json

class PeopleClientError(Exception):
    pass


class PeopleClient:

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def get_all(self, limit = None):
        response = requests.get(self.base_url)

        if limit is None:
            return response.json()

        if limit <= 0:
            raise ValueError('Limit has to be positive.')

        response = requests.get(self.base_url, params={'_limit': limit})

        total_records = int(response.headers['X-Total-Count'])
        pages_count = total_records // limit
        if total_records % limit != 0:
            pages_count += 1
        people = response.json()
        for page in range(2, pages_count+1):
            chunk = requests.get(self.base_url, params={'_limit': limit, '_page': page}).json()

            for person in chunk:
                people.append(person)
        return people

    def person_by_id(self, person_id):
        url = self.base_url + str(person_id)
        response = requests.get(url)
        if response.status_code == 404:
            raise PeopleClientError('User with given id not found')
        elif not response.ok:
            raise PeopleClientError('Unknow error')
        return response.json()

    def query(self, **criteria):

        fields_names = ('first_name', 'last_name', 'email', 'phone', 'ip_address')

        for key, value in criteria.items():
            if key not in fields_names:
                raise ValueError('Unknown key is: ' + key)

        response = requests.get(self.base_url, params=criteria)
        return response.json()

    def people_by_partial_ip(self, partial_ip):

        reg_partial_ip = '^' + partial_ip
        response = requests.get(self.base_url, params={'ip_address_like': reg_partial_ip})
        return response.json()


    def add_person(self, first_name, last_name, email, phone, ip_address):

        headers = {'Authorization': 'Bearer ' + self.token}
        person = {'first_name': first_name, 'last_name': last_name,
                    'email': email, 'phone': phone, 'ip_address': ip_address}

        response = requests.post(self.base_url, json=person, headers=headers)

        if response.status_code != 201:
            raise PeopleClientError(response.json()['error'])
        return response.json()

    def delete_by_id(self, person_id):
        headers = {'Authorization': 'Bearer' + self.token}

        url = self.base_url + str(person_id)
        response = requests.delete(url, headers=headers)

        if response.status_code == 404:
            raise PeopleClientError('User with given id not found')
        elif not response.ok:
            raise PeopleClientError('Unknown error')
        return response.json()

    def delete_by_name(self, first_name):

        headers = {'Authorization': 'Bearer' + self.token}
        mynames = []
        count = 0
        response1 = requests.get(self.base_url).json()

        for record in response1:
            if record['first_name'] == first_name:
                mynames.append(record)
                count += 1
        print(count)

        for name in mynames:
            # response = requests.get(self.base_url, json= name, headers= headers) - metoda przechodzi response.stauts_code = 200
            response = requests.delete(self.base_url, json=name, headers=headers)  # response.status_code = 404
            print(response)
            if response.status_code == 404:
                raise PeopleClientError('User with given name not found')
            elif not response.ok:
                raise PeopleClientError('Unknown error')
            return response.json(), count

    def add_from_file(self, my_file):
        headers = {'Authorization': 'Bearer' + self.token}

        with open(my_file, 'rt') as out_file:
            persons = json.load(out_file)

        for person in persons:
            response = requests.post(self.base_url, json=person, headers=headers)
        return response.json

        if response.status_code != 201:
                raise PeopleClientError(response.json()['error'])
        return response.json()


if __name__ == '__main__':
    token = hashlib.md5('relayr'. encode('ascii')).hexdigest()
    client = PeopleClient('http://polakow.eu:3000/people/', token)
    people = client.get_all()
    people2 = client.get_all(200)
    people5 = client.query(first_name='Tatiana')
    people7 = client.delete_by_id('22')
    people9 = client.delete_by_name('John')
    people10 = client.add_from_file('data.json')
    print(people)
    print(people == people2)
    people3 = client.add_person('Marek', 'Drama', 'jondram@agmail.com', '+48505789456', '192.168.1.1')
    print(people3)
    people4 = client.person_by_id('22')
    print(people4)

    print(people5)
    people6 = client.people_by_partial_ip('192.168')
    print(people6)