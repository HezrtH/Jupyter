import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def execute_query(cursor, query):
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        print(row)

server = 'THINHDEPTRAI\SQLEXPRESS'
database = 'CHICAGO_DATA'

connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'

# Tạo kết nối
try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
except pyodbc.Error as e:
    print(f"Error connecting to the database: {str(e)}")
    exit()

# Problem 1
def problem_1():
    query = 'SELECT COUNT(*) FROM CHICAGO_CRIME'
    execute_query(cursor, query)

# Problem 2
def problem_2():
    query = '''
        SELECT CC.[Community_Area_Name], CC.[Per_Capita_Income]
        FROM CHICAGO_CENSUS CC
        JOIN CHICAGO_CRIME CR
        ON CC.[Community_Area_Number] = CR.[Community_Area]
        WHERE CC.[Per_Capita_Income] < 11000
    '''
    execute_query(cursor, query)

# Problem 3
def problem_3():
    query = '''
            SELECT [Case_Number], [Description]
            FROM CHICAGO_CRIME
            WHERE [Description] LIKE '%child%' OR [Description] LIKE '%minor%'
        '''
    execute_query(cursor, query)

# Problem 4
def problem_4():
    query = '''SELECT [Case_Number], [Description] 
               FROM CHICAGO_CRIME 
               WHERE [Primary_Type] LIKE '%KIDNAPPING%' AND [Description] LIKE '%child%'
    '''
    execute_query(cursor, query)

# Problem 5
def problem_5():
    query = '''
        SELECT DISTINCT [Primary_Type]
        FROM CHICAGO_CRIME
        WHERE [Location_Description] LIKE '%SCHOOL%'
    '''
    execute_query(cursor, query)

# Problem 6
def problem_6():
    query = '''SELECT [Elementary_Middle_or_High_School], AVG(CONVERT(FLOAT, [Safety_Score])) AS AverageSafetyScore 
               FROM CHICAGO_SCHOOL
               GROUP BY [Elementary_Middle_or_High_School]
               '''
    execute_query(cursor, query)

# Problem 7
def problem_7():
    query = '''
        SELECT TOP 5 [Community_Area_Name], [Percent_Households_Below_Poverty]
        FROM CHICAGO_CENSUS
        ORDER BY [Percent_Households_Below_Poverty] DESC
    '''
    execute_query(cursor, query)

# Problem 8
def problem_8():
    query = '''
        SELECT TOP 1 CR.[Community_Area], COUNT(*) AS CrimeCount
        FROM CHICAGO_CRIME CR join CHICAGO_CENSUS CC
        ON CR.[Community_Area] = CC.[Community_Area_Number]
        GROUP BY CC.[Community_Area_Name], CR.[Community_Area]
        ORDER BY CrimeCount DESC
    '''
    execute_query(cursor, query)
# Problem 9
def problem_9():
    query = '''
        SELECT [Community_Area_Name], [Community_Area_Number], [Hardship_Index]
        FROM CHICAGO_CENSUS
        WHERE [Hardship_Index] = (SELECT MAX([Hardship_Index]) FROM CHICAGO_CENSUS)
    '''
    execute_query(cursor, query)

# Problem 10
def problem_10():
    query = '''
        SELECT [Community_Area_Name]
        FROM CHICAGO_CENSUS
        WHERE [Community_Area_Number] = (
                                SELECT TOP 1 CR.[Community_Area]
                                FROM CHICAGO_CRIME CR join CHICAGO_CENSUS CC
                                ON CR.[Community_Area] = CC.[Community_Area_Number]
                                GROUP BY CC.[Community_Area_Name], CR.[Community_Area]
                                ORDER BY COUNT(*) DESC
                        );
    '''
    execute_query(cursor, query)

# Biểu đồ số lượng tội phạm theo từng loại hình
def graph1():

    query = 'SELECT [Primary_Type], COUNT(*) as Count FROM CHICAGO_CRIME GROUP BY [Primary_Type]'
    data = pd.read_sql_query(query, connection)

    plt.figure(figsize=(20, 12))
    plt.bar(data['Primary_Type'], data['Count'])
    plt.xlabel('Loại Tội phạm')
    plt.ylabel('Số lượng')
    plt.title('Biểu đồ số lượng tội phạm theo loại')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# Biểu đồ số lượng tội phạm theo năm và theo loại hình
def graph2():

    query = """
        SELECT [Year], [Primary_Type], COUNT(*) as [Crime_Count]
        FROM CHICAGO_CRIME
        Where [Year] <= 2002
        GROUP BY [Year], [Primary_Type]
        ORDER BY [Year]
    """

    data = pd.read_sql_query(query, connection)

    plt.figure(figsize=(18, 10))
    for primary_type, group in data.groupby('Primary_Type'):
        plt.plot(group['Year'], group['Crime_Count'], label=primary_type)
    plt.xlabel('Năm')
    plt.ylabel('Số lượng tội phạm')
    plt.title('Biểu đồ số lượng tội phạm theo năm và theo loại hình')
    plt.legend(loc='upper left', bbox_to_anchor=(0.8, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Biểu đồ phần trăm tội phạm theo loại
def graph3():

    query = 'SELECT [Primary_Type], COUNT(*) as Count FROM CHICAGO_CRIME GROUP BY [Primary_Type]'
    data = pd.read_sql_query(query, connection)

    plt.figure(figsize=(8, 8))
    plt.pie(data['Count'], labels=data['Primary_Type'], autopct='%1.1f%%', startangle=140)
    plt.title('Biểu đồ phần trăm tội phạm theo loại')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# Biểu đồ Violin Plot cho số lượng tội phạm theo năm
def graph4():

    query = '''
        SELECT [Primary_Type], [Year] FROM CHICAGO_CRIME
        WHERE [Primary_Type] IN ('THEFT', 'BATTERY', 'NARCOTICS', 'BURGLARY')
    '''
    data = pd.read_sql_query(query, connection)

    plt.figure(figsize=(10, 6))
    sns.violinplot(x='Primary_Type', y='Year', data=data)
    plt.xlabel('Loại Tội phạm')
    plt.ylabel('Năm')
    plt.title('Biểu đồ Violin Plot cho số lượng tội phạm theo năm')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Biểu đồ StackArea cho các loại hình phạm tội qua năm
def graph5():

    query = '''
        SELECT YEAR([Date]) AS [Year], [Primary_Type], COUNT(*) AS [Crime_Count]
        FROM CHICAGO_CRIME
        WHERE [YEAR] > 2000 and [YEAR] < 2007
        GROUP BY YEAR([Date]), [Primary_Type]
        ORDER BY YEAR([Date])
    '''

    data = pd.read_sql_query(query, connection)

    # Pivot dữ liệu để có thể vẽ biểu đồ stack area
    pivot_data = data.pivot(index='Year', columns='Primary_Type', values='Crime_Count')

    pivot_data.plot(kind='area', stacked=True)
    plt.xlabel('Year')
    plt.ylabel('Crime Count')
    plt.title('Biểu đồ StackArea cho các loại hình phạm tội qua năm')
    plt.legend(loc='upper left', bbox_to_anchor= (0.83,1))
    plt.show()


def main():
    while True:
        print("\nMenu:")
        print("1. Total number of crimes recorded")
        print("2. Community areas with per capita income less than 11000")
        print("3. List all case numbers for crimes involving minors")
        print("4. List all kidnapping crimes involving a child")
        print("5. What kind of crimes were recorded at schools")
        print("6. List the average safety score for all types of schools")
        print("7. List 5 community areas with highest % of households below poverty line")
        print("8. Which community area(number) is most crime-prone")
        print("9. Find the name of the community area with the highest hardship index")
        print("10. Determine the Community Area Name with most number of crimes")
        print("11. Biểu đồ số lượng tội phạm theo từng loại hình" )
        print("12. Biểu đồ số lượng tội phạm theo năm")
        print("13. Biểu đồ phần trăm tội phạm theo loại")
        print("14. Biểu đồ Violin Plot cho số lượng tội phạm theo năm")
        print("15. Biểu đồ StackArea cho các loại hình phạm tội qua năm")
        print("16. Kết thúc")

        choice = input("Chọn 1 số (1 -> 16): ").strip()
        if choice == '1':
            problem_1()
        elif choice == '2':
            problem_2()
        elif choice == '3':
            problem_3()
        elif choice == '4':
            problem_4()
        elif choice == '5':
            problem_5()
        elif choice == '6':
            problem_6()
        elif choice == '7':
            problem_7()
        elif choice == '8':
            problem_8()
        elif choice == '9':
            problem_9()
        elif choice == '10':
            problem_10()
        elif choice == '11':
            graph1()
        elif choice == '12':
            graph2()
        elif choice == '13':
            graph3()
        elif choice == '14':
            graph4()
        elif choice == '15':
            graph5()
        elif choice == '16':
            break

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
