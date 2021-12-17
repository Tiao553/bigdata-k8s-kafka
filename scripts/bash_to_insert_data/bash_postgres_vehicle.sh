cd "/home/sebastiao/projects/luan/chalanger_kafka/scripts/create_tables_postgres"

for i in {1..100}
do
   python3.9 insert_vehicle_postgres.py
done