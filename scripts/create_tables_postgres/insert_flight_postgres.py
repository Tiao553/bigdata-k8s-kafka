import os
import time
import argparse
import pandas as pd
import numpy as np
from faker import Faker
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv
from faker_airtravel import AirTravelProvider

load_dotenv()

url_conection = os.environ.get("POSTGRES")

# função para parsear a saída do parâmetro SILENT
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# Instancia a classe Faker
faker = Faker()
faker.add_provider(AirTravelProvider)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate fake data...')

    parser.add_argument('--interval', type=int, default=0.005,
                        help='interval of generating fake data in seconds')
    parser.add_argument('-n', type=int, default=1,
                        help='sample size')
    parser.add_argument('--connection-string', '-cs', dest="connection_string", 
                        type=str, default=f'{url_conection}',
                        help='Connection string to the database')
    parser.add_argument('--silent', type=str2bool, nargs='?',
                        const=True, default=False,
                        help="print fake data")

    args = parser.parse_args()

    print(f"Args parsed:")
    print(f"Interval: {args.interval}")
    print(f"Sample size; {args.n}")
    print(f"Connection string: {args.connection_string}", end='\n\n')

    #-----------------------------------------------------------------

    engine = create_engine(args.connection_string)

    print("Iniciando a simulacao...", end="\n\n")

    # Gera dados fake a faz ingestão
    while True:
        customer_id   = [faker.random_int() for i in range(args.n)]
        aeroporto    = [faker.airport_name() for i in range(args.n)]
        linha_aerea    = [faker.airline() for i in range(args.n)]
        cod_iata   = [faker.airport_iata() for i in range(args.n)]
        dt_update  = [datetime.now() for i in range(args.n)]

        df = pd.DataFrame({
            "customer_id":customer_id,
            "aeroporto": aeroporto,
            "linha_aerea": linha_aerea,
            "cod_iata": cod_iata,
            "dt_update": dt_update
        })

        df.to_sql("flight", con=engine, if_exists="append", index=False)

        if not args.silent:
            print(df, end="\n\n")

        time.sleep(args.interval)