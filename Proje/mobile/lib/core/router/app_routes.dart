class AppRoutes {
  AppRoutes._();

  static const String restaurantIdParam = 'id';

  // Route names
  static const String splashName = 'splash';
  static const String loginName = 'login';
  static const String registerName = 'register';
  static const String homeName = 'home';
  static const String orderUploadName = 'orderUpload';
  static const String orderHistoryName = 'orderHistory';
  static const String incidentReportName = 'incidentReport';
  static const String myIncidentsName = 'myIncidents';
  static const String restaurantListName = 'restaurantList';
  static const String riskyRestaurantsName = 'riskyRestaurants';
  static const String restaurantDetailName = 'restaurantDetail';
  static const String profileName = 'profile';

  // Static paths
  static const String splashPath = '/splash';
  static const String loginPath = '/login';
  static const String registerPath = '/register';
  static const String homePath = '/home';
  static const String orderUploadPath = '/orders/upload';
  static const String orderHistoryPath = '/orders/history';
  static const String incidentReportPath = '/incidents/report';
  static const String myIncidentsPath = '/incidents/my';
  static const String restaurantListPath = '/restaurants';
  static const String riskyRestaurantsPath = '/restaurants/risky';
  static const String restaurantDetailPathPattern = '/restaurants/:id';
  static const String profilePath = '/profile';

  // Dynamic paths
  static String restaurantDetailPath(int restaurantId) =>
      '/restaurants/$restaurantId';

    static Map<String, String> restaurantDetailParameters(int restaurantId) =>
      {restaurantIdParam: restaurantId.toString()};
}
