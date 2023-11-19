from datetime import time


class Solve():
    def __init__(self):
        self.orders = []
        self.commands = []
        self.revenue_of_shop = {}
        self.revenue_of_shop_to_each_customer = {}
        self.orders_by_time = {}
        self.input()
        self.process()

    def input(self):
        while True:
            line = input().strip()
            if line == '#':
                break
            else:
                self.orders.append(list(map(lambda x: x.strip(), line.split())))

        while True:
            line = input().strip()
            if line == '#':
                break
            else:
                self.commands.append(list(map(lambda x: x.strip(), line.split())))

    def process(self):
        for order in self.orders:
            self.revenue_of_shop[order[3]] = self.revenue_of_shop.get(order[3], 0) + int(order[2])
            revenue_of_shop = self.revenue_of_shop_to_each_customer.get(order[3], {})
            revenue_of_cus = revenue_of_shop.get(order[0], 0)
            revenue_of_cus += int(order[2])
            revenue_of_shop[order[0]] = revenue_of_cus
            self.revenue_of_shop_to_each_customer[order[3]] = revenue_of_shop

            # Change the time to time object
            hour, minute, second = map(int, order[4].split(':'))
            order[4] = time(hour, minute, second)

            # Add order to the orders_by_time data structure
            time_range = (order[4], order[4])
            if time_range in self.orders_by_time:
                self.orders_by_time[time_range].append(order)
            else:
                self.orders_by_time[time_range] = [order]

    def solve(self):
        for command in self.commands:
            if command[0] == '?total_number_orders':
                print(len(self.orders))
            elif command[0] == '?total_revenue':
                print(sum([int(order[2]) for order in self.orders]))
            elif command[0] == '?total_consume_of_customer_shop':
                print(self.revenue_of_shop_to_each_customer[command[2]][command[1]])
            elif command[0] == '?revenue_of_shop':
                print(self.revenue_of_shop.get(command[1], 0))
            elif command[0] == '?total_revenue_in_period':
                res = 0
                start_time = time(*map(int, command[1].split(':')))
                end_time = time(*map(int, command[2].split(':')))

                for time_range in self.orders_by_time:
                    if start_time <= time_range[1] and end_time >= time_range[0]:
                        orders = self.orders_by_time[time_range]
                        for order in orders:
                            res += int(order[2])
                print(res)


if __name__ == '__main__':
    solver = Solve()
    solver.solve()
