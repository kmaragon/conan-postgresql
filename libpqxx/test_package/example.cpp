#include <iostream>
#include <pqxx/pqxx>

int main() {
    try
    {
        pqxx::connection conn;
        std::cout << "Connected to " << conn.dbname() << std::endl;
    }
    catch (const std::exception& e)
    {
        std::cout << "Didn't connect to DB but lib still worked: " << e.what() << std::endl;
    }

    return 0;
}
