#include <iostream>
#include "libpq-fe.h"

int main() {
    auto* result = PQconnectdb("user=pgsql dbname=mydb port=5432");
    std::cout << "Result is " << result << std::endl;
    return 0;
}
